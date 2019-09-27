# Model the fit results with a function
# Derek Fujimoto
# August 2019

from tkinter import *
from tkinter import ttk, messagebox
from functools import partial

import logging,re,os,warnings
import numpy as np
import pandas as pd
import bdata as bd
import weakref as wref

from bfit import logger_name
from bfit.backend.entry_color_set import on_focusout,on_entry_click
from bfit.backend.raise_window import raise_window
from bfit.backend.ConstrainedFunction import ConstrainedFunction as CstrFnGenerator

import bfit.backend.colors as colors

from bfit.fitting.fit_bdata import fit_list

# ========================================================================== #
class popup_fit_constraints(object):
    """
        Popup window for modelling the fit results with a function
        
        bfit
        fittab
        logger
        
        constr_text:        string, text defining constraints
        entry:              Text, text entry for user
        new_par:            dataframe, index: parnames, columns: p0,blo,bhi,res,err
        
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
    
    # default parameter values on new parameter
    default_parvals = { 'p0':1,
                        'blo':-np.inf,
                        'bhi':np.inf,
                        'res':np.nan,
                        'err':np.nan}

    # ====================================================================== #
    def __init__(self,bfit,constr_text='',output_par_text='',output_text=''):
        self.bfit = bfit
        self.fittab = bfit.fit_files
        self.constr_text = constr_text
        self.output_par_text_val = output_par_text
        
        if not output_text:
            self.output_text_val = {}
        else:
            self.output_text_val = output_text
    
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Fit With Constrained Parameters')
        frame = ttk.Frame(self.win,relief='sunken',pad=5)
        left_frame = ttk.Frame(frame)
        right_frame = ttk.Frame(frame)

        # set icon
        try:
            img = PhotoImage(file=os.path.dirname(__file__)+'/../images/icon.gif')
            self.win.tk.call('wm', 'iconphoto', self.win._w, img)
        except Exception as err:
            print(err)

        # Key bindings
        self.win.bind('<Control-Key-Return>',self.do_fit)
        self.win.bind('<Control-Key-KP_Enter>',self.do_fit)

        # Keyword parameters
        key_param_frame = ttk.Frame(left_frame,relief='sunken',pad=5)
        s = 'Reserved variable names:\n\n'
        self.reserved_pars = CstrFnGenerator.keyvars
        
        keys = list(self.reserved_pars.keys())
        descr = [self.reserved_pars[k] for k in self.reserved_pars]
        maxk = max(list(map(len,keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk),d) for k,d in zip(keys,descr)])
        s += '\n'
        key_param_label = ttk.Label(key_param_frame,text=s,justify=LEFT)
        
        # fit parameter names 
        fit_param_frame = ttk.Frame(left_frame,relief='sunken',pad=5)
        s = 'Reserved function parameter names:\n\n'
        self.parnames = self.fittab.fitter.gen_param_names(
                                        self.fittab.fit_function_title.get(),
                                        self.fittab.n_component.get())
        
        s += '\n'.join([k for k in sorted(self.parnames)]) 
        s += '\n'
        fit_param_label = ttk.Label(fit_param_frame,text=s,justify=LEFT)

        # module names 
        module_frame = ttk.Frame(left_frame,relief='sunken',pad=5)
        s = 'Reserved module names:\n\n'
        
        keys = list(self.modules.keys())
        descr = [self.modules[k] for k in self.modules]
        maxk = max(list(map(len,keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk),d) for k,d in zip(keys,descr)])
        s += '\n'
        modules_label = ttk.Label(module_frame,text=s,justify=LEFT)
        
        # Text entry
        entry_frame = ttk.Frame(right_frame,relief='sunken',pad=5)
        entry_label = ttk.Label(entry_frame,justify=LEFT,
                                text='Enter one constraint equation per line.'+\
                                     '\nNon-reserved words are shared variables.'+\
                                     '\nEx: "1_T1 = a*np.exp(b*BIAS**0.5)+c"'+\
                                     '\nNote: Shared and fixed flags from main window ignored.')
        self.entry = Text(entry_frame,width=60,height=13,state='normal')
        self.entry.bind('<KeyRelease>',self.get_input)
        scrollb = Scrollbar(entry_frame, command=self.entry.yview)
        self.entry['yscrollcommand'] = scrollb.set
        
        # Insert default text
        self.entry.insert('1.0',self.constr_text.strip())
        
        # text for output
        output_frame = ttk.Frame(right_frame,relief='sunken',pad=5)
        output_head1_label = ttk.Label(output_frame,text='Par Name')
        output_head2_label = ttk.Label(output_frame,text='p0')
        output_head3_label = ttk.Label(output_frame,text='Bounds')
        output_head4_label = ttk.Label(output_frame,text='Result')
        output_head5_label = ttk.Label(output_frame,text='Error')
        self.output_par_text = Text(output_frame,width=8,height=8)
        self.output_text = {k:Text(output_frame,width=8,height=8,wrap='none')\
                            for k in ('p0','blo','bhi','res','err')}
        
        # default starter strings
        if self.output_par_text_val: 
            self.output_par_text.insert('1.0',self.output_par_text_val)
        self.output_par_text.config(state='disabled')
    
        if self.output_text_val: 
            for k in self.output_text_val:
                self.output_text[k].insert('1.0',self.output_text_val[k])

        # disable results
        for k in ('res','err'):
            self.output_text[k].config(state='disabled',width=12)

        # key bindings and scrollbar
        scrollb_out = Scrollbar(output_frame, command=self.yview)
        self.output_par_text['yscrollcommand'] = scrollb_out.set
        for k in self.output_text:
            self.output_text[k].bind('<KeyRelease>',self.get_result_input)
            self.output_text[k]['yscrollcommand'] = scrollb_out.set
                
        c = 0; r = 0;
        output_head1_label.grid(column=c,row=r);        c+=1;
        output_head2_label.grid(column=c,row=r);        c+=1;
        output_head3_label.grid(column=c,row=r,
                                columnspan=2);          c+=2;
        output_head4_label.grid(column=c,row=r);        c+=1;
        output_head5_label.grid(column=c,row=r);        c+=1;
        
        c = 0; r += 1;
        self.output_par_text.grid(column=c,row=r,sticky=N); c+=1;
        for k in ('p0','blo','bhi','res','err'):
            self.output_text[k].grid(column=c,row=r,sticky=N); c+=1;
        scrollb_out.grid(row=r, column=c, sticky='nsew')
        
        # fitting button 
        fit_button = ttk.Button(right_frame,text='Fit',command=self.do_fit)
        
        # gridding
        key_param_label.grid(column=0,row=0)
        fit_param_label.grid(column=0,row=0)
        modules_label.grid(column=0,row=0)
        entry_label.grid(column=0,row=0,sticky=W)
        self.entry.grid(column=0,row=1)
        scrollb.grid(row=1, column=1, sticky='nsew')
        
        # grid to frame
        frame.grid(column=0,row=0)
        left_frame.grid(column=0,row=0,sticky=(N,S))
        right_frame.grid(column=1,row=0,sticky=(N,S))
        
        key_param_frame.grid(column=0,row=0,rowspan=1,sticky=(E,W),padx=1,pady=1)
        module_frame.grid(column=0,row=1,sticky=(E,W),padx=1,pady=1,rowspan=2)
        fit_param_frame.grid(column=0,row=3,sticky=(E,W,N,S),padx=1,pady=1)
        
        entry_frame.grid(column=0,row=0,sticky=(N,E,W),padx=1,pady=1)
        output_frame.grid(column=0,row=1,sticky=(N,E,W,S),padx=1,pady=1)
        fit_button.grid(column=0,row=2,sticky=(N,E,W),padx=1,pady=1)
        
        # initialize 
        self.new_par = pd.DataFrame(columns=['name','p0','blo','bhi','res','err']) 
        
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
    
    # ====================================================================== #
    def do_fit(self,*args):
        """
            Set up the fit functions and do the fit. Then map the outputs to the
            proper displays. 
        """
        
        # parse text
        self.do_parse()
        
        # clean input
        text = self.constr_text.split('\n')
        text = [t.strip() for t in text if '=' in t]
        
        # check for no input
        if not text:    return
        
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
        cgen= CstrFnGenerator(self.bfit,alldef,eqn,allpar,self.parnames)
        
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
            
            genf,genc = cgen(data=data,fn=fn)
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
        runs = [int(k.split('.')[1]) for k in keylist]
        years = [int(k.split('.')[0]) for k in keylist]
        npar = len(sharelist)
        bounds = [[l,h] for l,h in zip(blo,bhi)]
        
        # do the fit and kill fitting window
        fit_status_window = fit_files.make_fit_status_window()
        try:
            par,cov,chi,gchi = fit_list(runs=runs,
                                        years=years,
                                        fnlist=fitfns,
                                        sharelist=sharelist,
                                        npar=npar,
                                        p0=p0,
                                        bounds=bounds,
                                        asym_mode='c',
                                        rebin=rebin,
                                        omit=omit,
                                        xlims=None,
                                        hist_select=self.bfit.hist_select)
        except Exception as errmsg:
            self.logger.exception('Fitting error')
            messagebox.showerror("Error",str(errmsg))
            raise errmsg from None
        finally:
            fit_status_window.destroy()
            del fit_status_window
        std = np.array(list(map(np.diag,cov)))**0.5
        
        # display output for global parameters
        for i in self.new_par.index:
            self.new_par.loc[i,'res'] = par[0][i]
            self.new_par.loc[i,'err'] = std[0][i]
        self.set_par_text()
        
        # calculate original parameter equivalents
        for i,k in enumerate(keylist):
            data = fetch_files.data_lines[k].bdfit
            
            # calculate
            old_par = [cfn(*par[i]) for cfn in constr_fns[i]]
            old_std = [st if adef not in defined else np.nan for st,adef in zip(std[i],alldef)]
            old_std += [np.nan]*(len(alldef)-len(old_std))
            old_chi = chi[i]
            
            # sort by original parameter name order
            old_std = [old_std[alldef.index(n)] for n in cgen.oldpar]
            
            # set to fitdata containers
            # [(parname),(par),(err),chi,fnpointer]
            data.set_fitresult([cgen.oldpar,old_par,old_std,old_chi,fnptrs[i]])
            
        # display in fit_files tab
        for key in fit_files.fit_lines:
            fit_files.fit_lines[key].show_fit_result()
        
        # show global chi
        fit_files.gchi_label['text'] = str(np.around(gchi,2))

        # do end-of-fit stuff
        fit_files.do_end_of_fit()
    
    # ====================================================================== #
    def do_parse(self,*args):
        """
            Detect new global variables
            returns split lines, new parameter names 
        """
        
        # clean input
        text = self.constr_text.split('\n')
        text = [t.strip() for t in text if '=' in t]
        
        # check for no input
        if not text:
            return
        
        # get equations and defined variables
        defined = [t.split('=')[0].strip() for t in text]
        eqn = [t.split('=')[1].strip() for t in text]
        
        # check for new parameters
        new_par = []
        for eq in eqn:
            lst = re.split('\W+',eq)    # split list non characters
            
            # throw out known things: numbers numpy equations
            delist = []
            for i,l in enumerate(lst):
                
                # check numpy functions
                if l == 'np':
                    delist.append(i)
                    delist.append(i+1)
                    continue
                
                # check integer
                try: 
                    int(l)
                except ValueError:
                    pass
                else:
                    delist.append(i)
                    continue
                
                # check variables
                if l in self.reserved_pars:  
                    delist.append(i)
                    continue
                    
            delist.sort()
            for i in delist[::-1]:
                try:
                    del lst[i]
                except IndexError:  # error raised on incomplete math: ex "np."
                    pass
                
            new_par.append(lst)

        # add result
        new_par = np.unique(np.concatenate(new_par))
        for k in new_par:
            
            # bad input
            if not k: continue
            
            # set defaults
            if k not in self.new_par['name'].values:
                self.new_par = self.new_par.append({'name':k,**self.default_parvals},
                                                   ignore_index=True)
        
        # drop results 
        for i,k in zip(self.new_par.index,self.new_par['name']):
            if k not in new_par:
                self.new_par.drop(i,inplace=True)
        
        # set fields
        self.new_par.sort_values('name',inplace=True)
        self.set_par_text()
        
        # logging
        self.logger.info('Parse found constraints for %s, and defined %s',
                         sorted(defined),
                         self.new_par['name'].values.tolist())
    
    # ====================================================================== #
    def get_input(self,*args):
        """Get input from text box."""
        self.constr_text = self.entry.get('1.0',END)
        self.do_parse()
        
    # ====================================================================== #
    def get_result_input(self,*args):
        """
            Set new_par row to match changes made by user
        """
    
        # get text
        try:
            text = {k:list(map(float,self.output_text[k].get('1.0',END).split('\n')[:-1])) \
                for k in self.output_text}
        # no update if blank
        except ValueError:
            return 
        
        # dataframe it
        try:
            text = pd.DataFrame(text)   
        # bad input
        except ValueError:
            return
        
        # get names of the parameters
        parnames = self.output_par_text.get('1.0',END).split('\n')[:-1]
        
        # update
        par = self.new_par.set_index('name')
        for i,name in enumerate(parnames):
            par.loc[name] = text.iloc[i]
        par.reset_index(inplace=True)
        self.new_par = par
        self.logger.debug('get_result_input: updated new_par')
    
    # ====================================================================== #
    def set_par_text(self):
        """
            Set the textboxes based on stored results in self.newpar
        """
        
        # get strings
        set_par = self.new_par.astype(str)
        
        # round
        numstr = '%'+('.%df' % self.bfit.rounding)
        for k in ('res','err'):
            set_par[k] = set_par.loc[:,k].apply(\
                    lambda x: numstr % np.around(float(x),self.bfit.rounding))
        
        # enable setting
        for k in ('res','err'):
            self.output_text[k].config(state='normal')
        self.output_par_text.config(state='normal')
        
        self.output_par_text.delete('1.0',END)
        self.output_par_text.insert(1.0,'\n'.join(set_par['name']))
        self.output_par_text_val = '\n'.join(set_par['name'])
        
        for k in self.output_text:
            self.output_text[k].delete('1.0',END)
            self.output_text[k].insert(1.0,'\n'.join(set_par[k]))
            self.output_text_val[k] = '\n'.join(set_par[k])
                
        # disable setting
        for k in ('res','err'):
            self.output_text[k].config(state='disabled')
        self.output_par_text.config(state='disabled')
        
    # ====================================================================== #
    def yview(self,*args):
        """
            Scrollbar for all output text fields
        """
        self.output_par_text.yview(*args)
        for k in self.output_text:
            self.output_text[k].yview(*args)
