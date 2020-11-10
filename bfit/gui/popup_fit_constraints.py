# Model the fit results with a function
# Derek Fujimoto
# Nov 2019


from tkinter import *
from tkinter import ttk
from functools import partial

import logging,re,os,warnings
import numpy as np
import pandas as pd
import bdata as bd

from bfit.backend.ConstrainedFunction import ConstrainedFunction as CstrFnGenerator
from bfit.fitting.fit_bdata import fit_bdata
from bfit.gui.template_fit_popup import template_fit_popup

# ========================================================================== #
class popup_fit_constraints(template_fit_popup):
    """
        Popup window for modelling the fit results with a function
        
        bfit
        fittab
        logger
        
        output_par_text     text, detected parameter names
        output_text         dict, keys: p0,blo,bhi,res,err, value: tkk.Text objects
       
        output_par_text_val string, contents of output_par_text
        output_text_val     dict of strings, contents of output_text
       
        parnames:           list, function inputs
        reserved_pars:      dict, define values in bdata that can be accessed
        win:                Toplevel
    """

    # names of modules the constraints have access to
    modules = {'np':'numpy'}
    
    window_title = 'Fit data with contrained parameters'
    
    # ====================================================================== #
    def __init__(self,bfit,constr_text='',output_par_text='',output_text=''):
        
        super().__init__(bfit,constr_text,output_par_text,output_text)
        
        # Keyword parameters
        key_param_frame = ttk.Frame(self.left_frame,relief='sunken',pad=5)
        s = 'Reserved variable names:\n\n'
        self.reserved_pars = CstrFnGenerator.keyvars
        
        keys = list(self.reserved_pars.keys())
        descr = [self.reserved_pars[k] for k in self.reserved_pars]
        maxk = max(list(map(len,keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk),d) for k,d in zip(keys,descr)])
        s += '\n'
        key_param_label = ttk.Label(key_param_frame,text=s,justify=LEFT)
        
        # fit parameter names 
        fit_param_frame = ttk.Frame(self.left_frame,relief='sunken',pad=5)
        s = 'Reserved function parameter names:\n\n'
        self.parnames = self.fittab.fitter.gen_param_names(
                                        self.fittab.fit_function_title.get(),
                                        self.fittab.n_component.get())
        
        s += '\n'.join([k for k in sorted(self.parnames)]) 
        s += '\n'
        fit_param_label = ttk.Label(fit_param_frame,text=s,justify=LEFT)

        # module names 
        module_frame = ttk.Frame(self.left_frame,relief='sunken',pad=5)
        s = 'Reserved module names:\n\n'
        
        keys = list(self.modules.keys())
        descr = [self.modules[k] for k in self.modules]
        maxk = max(list(map(len,keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk),d) for k,d in zip(keys,descr)])
        s += '\n'
        modules_label = ttk.Label(module_frame,text=s,justify=LEFT)
        
        # Text entry
        self.entry_label['text'] = 'Enter one constraint equation per line.'+\
                                 '\nNon-reserved words are shared variables.'+\
                                 '\nEx: "1_T1 = a*np.exp(b*BIAS**0.5)+c"'+\
                                 '\nNote: Shared and fixed flags from main window ignored.'
                
        # gridding
        key_param_label.grid(column=0,row=0)
        fit_param_label.grid(column=0,row=0)
        modules_label.grid(column=0,row=0)
        
        key_param_frame.grid(column=0,row=0,rowspan=1,sticky=(E,W),padx=1,pady=1)
        module_frame.grid(column=0,row=1,sticky=(E,W),padx=1,pady=1,rowspan=2)
        fit_param_frame.grid(column=0,row=3,sticky=(E,W,N,S),padx=1,pady=1)
        
    # ====================================================================== #
    def _do_fit(self,text):
        """
            Set up the fit functions and do the fit. Then map the outputs to the
            proper displays. 
        """
        
        # get equations and defined variables
        defined = [t.split('=')[0].strip() for t in text]
        eqn = [t.split('=')[1].strip() for t in text]
        
        # check that the defined variables all match function inputs
        for d in defined: 
            if d not in self.parnames:
                errmsg = 'Definition for "%s" invalid. ' % d+\
                         'Must only define function inputs. '
                messagebox.showerror("Error",errmsg)
                raise RuntimeError(errmsg)
        
        # make shared parameters for the rest of the parameters
        allpar = self.new_par['name'].tolist()
        alldef = defined[:]     # all parameter names in order
        sharelist = [True]*len(allpar)
        
        for n in sorted(self.parnames):
            if n not in defined:
                eqn.append(n)
                alldef.append(n)
                allpar.append(n)
                sharelist.append(False)
                        
        # replace 1_T1 with lambda1
        for i,_ in enumerate(allpar):
            if '1_T1' in allpar[i]:
                allpar[i] = allpar[i].replace('1_T1','lambda1')
        
        for i,_ in enumerate(eqn):
            while '1_T1' in eqn[i]:
                eqn[i] = eqn[i].replace('1_T1','lambda1')
                
        # make constrained functions
        cgen= CstrFnGenerator(alldef, eqn, allpar, self.parnames)
        
        # get the functions and initial parameters
        fit_files = self.bfit.fit_files
        fetch_files = self.bfit.fetch_files
        fitfns = []
        par = []
        rebin = []
        omit = []
        fnptrs = []
        constr_fns = []
        
        keylist = sorted(fit_files.fit_lines.keys())
        for k in keylist:
            line = fetch_files.data_lines[k]
            data = line.bdfit
            
            # get pulse length
            pulse_len = -1
            try:
                pulse_len = data.bd.get_pulse_s()
            except KeyError:
                pass
            
            # get function
            fn = fit_files.fitter.get_fn(fn_name=fit_files.fit_function_title.get(),
                                         ncomp=fit_files.n_component.get(),
                                         pulse_len=pulse_len,
                                         lifetime=bd.life[fit_files.probe_label['text']])
            
            genf, genc = cgen(data=data, fn=fn)
            fitfns.append(genf)
            fnptrs.append(fn)
            constr_fns.append(genc)
            
            # get initial parameters
            par.append(data.fitpar)
            
            # get rebin
            rebin.append(data.rebin.get())
            
            # get bin omission
            omit.append(data.omit.get())
        
        # clean up omit strings
        for i,om in enumerate(omit):
            if om == fetch_files.bin_remove_starter_line:
                omit[i] = ''
        
        # set up p0, bounds
        p0 = self.new_par['p0'].values
        blo = self.new_par['blo'].values
        bhi = self.new_par['bhi'].values
        
        p0 = [[p]*len(keylist) for p in p0]
        blo = [[p]*len(keylist) for p in blo]
        bhi = [[p]*len(keylist) for p in bhi]
                
        for n in sorted(self.parnames):
            if n not in defined:
                p0.append( [p['p0' ][n] for p in par])
                blo.append([p['blo'][n] for p in par])
                bhi.append([p['bhi'][n] for p in par])
        
        p0 = np.array(p0).T
        blo = np.array(blo).T
        bhi = np.array(bhi).T
        
        # set up fitter inputs
        npar = len(sharelist)
        bounds = [[l,h] for l,h in zip(blo,bhi)]
        data = [self.bfit.data[k] for k in keylist]
        kwargs = {'p0':p0, 'bounds':bounds}
        
        # get minimizer
        if 'trf'   in self.bfit.fit_files.fitter.__name__:  minimizer = 'trf'
        if 'minos' in self.bfit.fit_files.fitter.__name__:  minimizer = 'migradminos'
        if 'hesse' in self.bfit.fit_files.fitter.__name__:  minimizer = 'migradhesse'
            
        
        # do the fit and kill fitting window
        par, std_l, std_u, cov, chi, gchi = fit_bdata(
                                                data=data,
                                                fn=fitfns,
                                                shared=sharelist,
                                                asym_mode='c',
                                                rebin=rebin,
                                                omit=omit,
                                                xlims=None,
                                                hist_select=self.bfit.hist_select,
                                                minimizer=minimizer,
                                                **kwargs)
        
        # calculate original parameter equivalents
        for i,k in enumerate(keylist):
            data = fetch_files.data_lines[k].bdfit
            
            # calculate
            old_par = [cfn(*par[i]) for cfn in constr_fns[i]]
            old_std_l = [st if adef not in defined else np.nan for st, adef in zip(std_l[i], alldef)] 
            old_std_l += [np.nan]*(len(alldef)-len(old_std_l))
            
            old_std_u = [st if adef not in defined else np.nan for st, adef in zip(std_u[i], alldef)]
            old_std_u += [np.nan]*(len(alldef)-len(old_std_u))
            
            old_chi = chi[i]
            
            # sort by original parameter name order
            old_std_l = [old_std_l[alldef.index(n)] for n in cgen.oldpar]
            old_std_u = [old_std_u[alldef.index(n)] for n in cgen.oldpar]
            
            # set to fitdata containers
            # [(parname),(par),(err-),(err+),chi,fnpointer]
            data.set_fitresult([cgen.oldpar, old_par, old_std_l, old_std_u, old_chi, fnptrs[i]])
            
        # display in fit_files tab
        for key in fit_files.fit_lines:
            fit_files.fit_lines[key].show_fit_result()
        
        # show global chi
        fit_files.gchi_label['text'] = str(np.around(gchi, 2))

        # do end-of-fit stuff
        fit_files.do_end_of_fit()
        
        return (par[0,:], std_l[0,:], std_u[0,:])
