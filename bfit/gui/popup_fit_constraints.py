# Model the fit results with a function
# Derek Fujimoto
# Nov 2019


from tkinter import *
from tkinter import ttk, messagebox
from functools import partial

import logging, re, os, warnings
import numpy as np
import pandas as pd
import bdata as bd

from bfit.backend.ConstrainedFunction import ConstrainedFunction as CstrFnGenerator
from bfit.global_variables import KEYVARS
from bfit.gui.template_fit_popup import template_fit_popup
from bfit.gui.InputLine import InputLine


# ========================================================================== #
class popup_fit_constraints(template_fit_popup):
    """
        Popup window for settings fit parameters according to a function
        
        bfit
        fittab
        logger
        
        defined             list of str, defined parameter names
        eqn                 list of str, equations for each defined parameter
        
        label_new_var       Label, show new variables
        label_defined       Label, show which variables will be redefined
        
        new_par             list of list of str, new parameter found in each eqn
        new_par_unique      list of str, new parameters, sorted
        new_par_unique_old  list of str, new parameters, sorted at the last 
                            call of set_constrained
        
        output_par_text     text, detected parameter names
        output_text         dict, keys: p0, blo, bhi, res, err, value: tkk.Text objects
       
        output_par_text_val string, contents of output_par_text
        output_text_val     dict of strings, contents of output_text
       
        parnames:           list, function inputs
        reserved_pars:      dict, define values in bdata that can be accessed
        win:                Toplevel
    """

    # names of modules the constraints have access to
    modules = {'np':'numpy'}
    window_title = 'Constrain parameters'
    
    # ====================================================================== #
    def __init__(self, bfit, input_fn_text=''):
        
        super().__init__(bfit, input_fn_text)
        
        # initialize
        self.defined = None
        self.eqn = None
        self.new_par = None
        self.new_par_unique = None
        self.new_par_unique_old = None
        
        self.show()
        
    # ====================================================================== #
    def show(self):
        """
            show window
        """
        
        # show base class
        if not hasattr(self, 'win') or not Toplevel.winfo_exists(self.win):
            super().show()
        
        # Keyword parameters
        key_param_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        s = 'Reserved variable names:\n\n'
        self.reserved_pars = KEYVARS
        
        keys = list(self.reserved_pars.keys())
        descr = [self.reserved_pars[k] for k in self.reserved_pars]
        maxk = max(list(map(len, keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk), d) for k, d in zip(keys, descr)])
        s += '\n'
        key_param_label = ttk.Label(key_param_frame, text=s, justify=LEFT)
        
        # fit parameter names 
        fit_param_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        s = 'Reserved function parameter names:\n\n'
        self.parnames = self.fittab.fitter.gen_param_names(
                                        self.fittab.fit_function_title.get(), 
                                        self.fittab.n_component.get())
        
        s += '\n'.join([k for k in sorted(self.parnames)]) 
        s += '\n'
        fit_param_label = ttk.Label(fit_param_frame, text=s, justify=LEFT)

        # module names 
        module_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        s = 'Reserved module names:\n\n'
        
        keys = list(self.modules.keys())
        descr = [self.modules[k] for k in self.modules]
        maxk = max(list(map(len, keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk), d) for k, d in zip(keys, descr)])
        s += '\n'
        modules_label = ttk.Label(module_frame, text=s, justify=LEFT)
        
        # Text entry
        self.entry_label['text'] = 'Enter one constraint equation per line.'+\
                                 '\nNon-reserved words are shared variables.'+\
                                 '\nEx: "1_T1 = a*np.exp(b*BIAS**0.5)+c"'                                 
                
        # detected new parameters
        frame_detected = ttk.Frame(self.right_frame)
        label_defined_title = ttk.Label(frame_detected, text='Constrained parameters')
        label_new_var_title = ttk.Label(frame_detected, text='New variables')
        
        self.label_new_var = ttk.Label(frame_detected, text='')
        self.label_defined = ttk.Label(frame_detected, text='')
                
        # add constrain button
        button_constrain = ttk.Button(self.right_frame, text='Constrain', 
                                      command=self.set_constraints)
                
        # gridding
        key_param_label.grid(column=0, row=0)
        fit_param_label.grid(column=0, row=0)
        modules_label.grid(column=0, row=0)
        
        key_param_frame.grid(column=0, row=0, rowspan=1, sticky='ew', padx=1, pady=1)
        module_frame.grid(column=0, row=1, sticky='ew', padx=1, pady=1, rowspan=2)
        fit_param_frame.grid(column=0, row=3, sticky='ewns', padx=1, pady=1)
        
        frame_detected.grid(column=0, row=4, sticky='ewn', padx=1, pady=1)
        frame_detected.grid_columnconfigure(0, weight=1)
        frame_detected.grid_columnconfigure(1, weight=1)
        label_defined_title.grid(column=0, row=0, sticky='n', padx=1, pady=1)
        label_new_var_title.grid(column=1, row=0, sticky='n', padx=1, pady=1)
        self.label_defined.grid( column=0, row=1, sticky='n', padx=1, pady=1)
        self.label_new_var.grid( column=1, row=1, sticky='n', padx=1, pady=1)
        
        
        self.right_frame.grid_rowconfigure(4, weight=1)
        button_constrain.grid(column=0, row=5, sticky='ews', padx=1, pady=1)
        
    # ====================================================================== #
    def do_after_parse(self, defined=None, eqn=None, new_par=None):
        """
            show inputs as readback and save
        """
        
        if defined is not None:
        
            # check defined variables
            ncomp = self.bfit.fit_files.n_component.get()
            fn_name = self.bfit.fit_files.fit_function_title.get()
            par_names = self.bfit.fit_files.fitter.gen_param_names(fn_name, ncomp)
            s = [d if d else '<blank>' for d in sorted(defined)]
            s = [d if d in par_names else '%s [ERROR: Bad parameter]' % d for d in s]
            s = '\n'.join(s)
            
            # set label
            self.label_defined.config(text=s)
            
            # check new variables
            s = sorted(np.unique(np.concatenate(new_par)))
            s = [i for i in s if i and i not in self.parnames]
            
            # show input
            self.label_new_var.config(text='\n'.join(s))
        
        else:
            self.label_defined.config(text='')
            self.label_new_var.config(text='')
        
        # save
        self.defined = defined
        self.eqn = eqn
        self.new_par = new_par
        
        try:
            self.new_par_unique = sorted(np.unique(np.concatenate(new_par)))
        except TypeError:
            self.new_par_unique = None
    
    # ====================================================================== #
    def _do_fit(self, text):
        """
            Set up the fit functions and do the fit. Then map the outputs to the
            proper displays. 
        """
        
        self.logger.info('Starting fit')
        
        # get equations and defined variables
        defined = [t.split('=')[0].strip() for t in text]
        eqn = [t.split('=')[1].strip() for t in text]
        
        # check that the defined variables all match function inputs
        for d in defined: 
            if d not in self.parnames:
                errmsg = 'Definition for "%s" invalid. ' % d+\
                         'Must only define function inputs. '
                messagebox.showerror("Error", errmsg)
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
        for i, _ in enumerate(allpar):
            if '1_T1' in allpar[i]:
                allpar[i] = allpar[i].replace('1_T1', 'lambda1')
        
        for i, _ in enumerate(eqn):
            while '1_T1' in eqn[i]:
                eqn[i] = eqn[i].replace('1_T1', 'lambda1')
                
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
                pulse_len = data.bd.pulse_s
            except (KeyError, AttributeError):
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
        for i, om in enumerate(omit):
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
        bounds = [[l, h] for l, h in zip(blo, bhi)]
        data = [self.bfit.data[k] for k in keylist]
        kwargs = {'p0':p0, 'bounds':bounds}
        
        # get minimizer
        if 'trf'   in fit_files.fitter.__name__:  minimizer = 'trf'
        if 'minos' in fit_files.fitter.__name__:  minimizer = 'minos'
        if 'hesse' in fit_files.fitter.__name__:  minimizer = 'migrad'
        
        # set up queue for results
        que = Queue()
        
        # do fit
        def run_fit():
            try:
                out = fit_bdata(data=data, 
                                fn=fitfns, 
                                shared=sharelist, 
                                asym_mode='c', 
                                rebin=rebin, 
                                omit=omit, 
                                xlims=None, 
                                hist_select=self.bfit.hist_select, 
                                minimizer=minimizer, 
                                **kwargs)
            except Exception as err:
                que.put(str(err))
                raise err from None
                
            # par, std_l, std_u, cov, chi, gchi
            que.put(out)
            
        # start the fit
        def do_enable():
            fit_files.input_enable_disable(self.win, state='normal', first=False)
            fit_files.input_enable_disable(fit_files.fit_data_tab, state='normal')
        def do_disable():
            fit_files.input_enable_disable(self.win, state='disabled', first=False)
            fit_files.input_enable_disable(fit_files.fit_data_tab, state='disabled')
            
        popup = popup_ongoing_process(self.bfit, 
                    target = run_fit,
                    message="Constrained fit in progress...", 
                    queue = que,
                    do_disable = do_disable,
                    do_enable = do_enable,
                    )
            
        output = popup.run()
        
        # fit success
        if type(output) is tuple:
            par, std_l, std_u, cov, chi, gchi = output
            std_l = np.abs(std_l)
        
        # error
        elif type(output) is str:
            messagebox.showerror("Error", output)
            return 
        
        # fit cancelled
        elif output is None:
            return
            
        # check list depth
        try:
            par[0][0]
        except IndexError:
            par = np.array([par])
            std_l = np.array([std_l])
            std_u = np.array([std_u])
            chi = np.array([chi])
            
        # calculate original parameter equivalents
        for i, k in enumerate(keylist):
            data = fetch_files.data_lines[k].bdfit

            # calculate parameter values and estimate errors
            old_par = [cfn(*par[i]) for cfn in constr_fns[i]]
            old_std_l = [abs(p-cfn(*(par[i]-std_l[i]))) for p, cfn in zip(old_par, constr_fns[i])]
            old_std_u = [abs(p-cfn(*(par[i]+std_u[i]))) for p, cfn in zip(old_par, constr_fns[i])]
            
            old_chi = chi[i]
            
            # set to fitdata containers
            results = pd.DataFrame({'res': old_par, 
                                    'dres+': old_std_u,
                                    'dres-': old_std_l,
                                    'chi': old_chi,
                                    }, index=cgen.oldpar)
            data.set_fitresult({'fn': fnptrs[i], 'results': results, 'gchi': gchi})
            
        # display in fit_files tab
        for key in fit_files.fit_lines:
            fit_files.fit_lines[key].show_fit_result()
        
        # show global chi
        fit_files.gchi_label['text'] = str(np.around(gchi, 2))

        # do end-of-fit stuff
        fit_files.do_end_of_fit()
        
        self.logger.info('Fitting end')
        
        return (par[0, :], std_l[0, :], std_u[0, :])

    # ====================================================================== #
    def do_return(self, *_):
        """
            Activated on press of return key
        """
        self.set_constraints()
    
    # ====================================================================== #
    def set_constraints(self):
        """
            Set up constraining parameter functions
        """
        
        # no constraints: enable all lines
        if self.defined is None:
            for fline in self.fittab.fit_lines.values():
                
                # enable
                for line in fline.lines:
                    line.enable()
                    
                # delete unused parameters
                if self.new_par_unique_old is not None:
                    fline.data.fitpar.drop(self.new_par_unique_old, 
                                           axis='index', 
                                           inplace=True)
                        
                fline.data.constrained = []
                        
            # clean up
            self.new_par_unique_old = None
            self.fittab.populate()
            self.cancel()
            return
        
        # check for circular definitions
        for d, e in zip(self.defined, self.eqn):
            if d in e:
                msg = 'Circular parameter definitions not allowed:'+\
                      '\n{d} = f({d}) is not allowed'.format(d=d)
                messagebox.showerror('Error', msg)
                raise RuntimeError(msg)
        
        # check for more circular definitions
        for d in self.defined:
            for e in self.eqn:
                if d in e:
                    msg = 'Redefined parameter {p} cannot be used as an input'.format(p=d)
                    messagebox.showerror('Error', msg)
                    raise RuntimeError(msg)
        
        # disable lines
        for fline in self.fittab.fit_lines.values():
            for line in fline.lines:
                line.enable()
                if line.pname in self.defined:
                    line.variable['fixed'].set(False)
                    line.variable['shared'].set(False)
                    line.disable()
        
        # add lines and parameters
        n = len(self.new_par_unique)
        for fline in self.fittab.fit_lines.values():
            data = fline.data
            
            # delete unused parameters
            if self.new_par_unique_old is not None:
                data.fitpar.drop(self.new_par_unique_old, axis='index', inplace=True)
            
            # add new parameters
            cols = InputLine.columns
            new_fit_par = { cols[0]: np.ones(n),            # p0
                            cols[1]: np.full(n, -np.inf),   # blo    
                            cols[2]: np.full(n, np.inf),    # bhi
                            cols[3]: np.full(n, np.nan),    # res
                            cols[4]: np.full(n, np.nan),    # dres-
                            cols[5]: np.full(n, np.nan),    # dres+
                            cols[6]: np.full(n, np.nan),    # chi
                            cols[7]: np.full(n, False),     # fixed
                            cols[8]: np.full(n, False),     # shared
                            }
            data.set_fitpar(pd.DataFrame(new_fit_par, 
                                         index=self.new_par_unique)
                            )
                            
            # copy defined param to data
            data.constrained = self.defined
            
        # add runs
        self.fittab.populate()
        
        # save defined values
        self.new_par_unique_old = self.new_par_unique
        
        # close
        self.cancel()
