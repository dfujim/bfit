# Model the fit results with a function
# Derek Fujimoto
# August 2019

from tkinter import *
from tkinter import ttk, messagebox
from functools import partial

import logging,re
import numpy as np
import weakref as wref

from bfit import logger_name
from bfit.backend.entry_color_set import on_focusout,on_entry_click
from bfit.backend.raise_window import raise_window

import bfit.backend.colors as colors
import bfit.backend.ConstrainedFunction as CstrFn

# ========================================================================== #
class popup_fit_constraints(object):
    """
        Popup window for modelling the fit results with a function
        
        bfit
        fittab
        logger
        
        constr_text:        string, text defining constraints
        new_par:            list, parameter names of new, shared, inputs
        reserved_pars:      dict, define values in bdata that can be accessed
        parnames:           list, function inputs
        win:                Toplevel
        
    """

    # names of modules the constraints have access to
    modules = {'np':'numpy'}

    # ====================================================================== #
    def __init__(self,bfit,constr_text=''):
        self.bfit = bfit
        self.fittab = bfit.fit_files
        self.constr_text = constr_text
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Constrain Fit Parameters')
        frame = ttk.Frame(self.win,relief='sunken',pad=5)

        # Key bindings
        self.win.bind('<Return>',self.do_fit)             
        self.win.bind('<KP_Enter>',self.do_fit)
        
        # Keyword parameters
        key_param_frame = ttk.Frame(frame,relief='sunken',pad=5)
        s = 'Reserved variable names:\n\n'
        self.reserved_pars = CstrFn.ConstrainedFunction.keyvars
        
        keys = list(self.reserved_pars.keys())
        descr = [self.reserved_pars[k] for k in self.reserved_pars]
        maxk = max(list(map(len,keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk),d) for k,d in zip(keys,descr)])
        s += '\n'
        key_param_label = ttk.Label(key_param_frame,text=s,justify=LEFT)
        
        # fit parameter names 
        fit_param_frame = ttk.Frame(frame,relief='sunken',pad=5)
        s = 'Reserved function input names:\n\n'
        self.parnames = self.fittab.fitter.gen_param_names(
                                        self.fittab.fit_function_title.get(),
                                        self.fittab.n_component.get())
        s += '\n'.join([k for k in self.parnames]) 
        s += '\n'
        fit_param_label = ttk.Label(fit_param_frame,text=s,justify=LEFT)

        # module names 
        module_frame = ttk.Frame(frame,relief='sunken',pad=5)
        s = 'Reserved module names:\n\n'
        
        keys = list(self.modules.keys())
        descr = [self.modules[k] for k in self.modules]
        maxk = max(list(map(len,keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk),d) for k,d in zip(keys,descr)])
        s += '\n'
        modules_label = ttk.Label(module_frame,text=s,justify=LEFT)
        
        # Text entry
        entry_frame = ttk.Frame(frame,relief='sunken',pad=5)
        entry_label = ttk.Label(entry_frame,justify=LEFT,
                                text='Enter one constraint per line.'+\
                                     '\nNon-reserved words are shared variables.'+\
                                     '\nEx: "1_T1 = a*np.exp(b*BIAS**0.5)+c"')
        self.entry = Text(entry_frame,width=50,height=13,state='normal')
        self.entry.bind('<KeyRelease>',self.get_input)
        scrollb = Scrollbar(entry_frame, command=self.entry.yview)
        self.entry['yscrollcommand'] = scrollb.set
        
        
        # fit
        parse_button = ttk.Button(frame,text='Parse Input',command=self.do_parse)
        
        
        # ~ # text for output
        # ~ self.model_results_text = Text(frame,width=17,height=8,state='normal')
        # ~ self.model_errors_text = Text(frame,width=17,height=8,state='normal')
        
        # ~ self.model_results_text.insert('1.0',self.result_str)
        
        # gridding
        key_param_label.grid(column=0,row=0)
        fit_param_label.grid(column=0,row=0)
        modules_label.grid(column=0,row=0)
        entry_label.grid(column=0,row=0,sticky=W)
        self.entry.grid(column=0,row=1)
        scrollb.grid(row=1, column=1, sticky='nsew')
        
        # grid to frame
        frame.grid(column=0,row=0)
        
        key_param_frame.grid(column=0,row=0,rowspan=1,sticky=(E,W),padx=1,pady=1)
        module_frame.grid(column=0,row=1,sticky=(E,W),padx=1,pady=1)
        fit_param_frame.grid(column=0,row=2,sticky=(E,W),padx=1,pady=1)
        
        entry_frame.grid(column=1,row=0,sticky=(N),padx=1,pady=1)
        parse_button.grid(column=1,row=1,sticky=(N,E,W),padx=1,pady=1)
        
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
    
    # ====================================================================== #
    def do_fit(self,*args):
        pass
        
    # ====================================================================== #
    def do_parse(self,*args):
        """
            Detect new global variables
            returns split lines, new parameter names 
        """
        
        # clean input
        text = self.constr_text.split('\n')
        text = [t.strip() for t in text if '=' in t]
        
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
                
                # check function names, variables
                if l in self.parnames:  
                    delist.append(i)
                    continue
                if l in self.reserved_pars:  
                    delist.append(i)
                    continue
                    
            delist.sort()
            for i in delist[::-1]:
                del lst[i]
                
            new_par.append(lst)
                
        return (text,new_par)    
    
    # ====================================================================== #
    def get_input(self,*args):
        """Get input from text box."""
        self.constr_text = self.entry.get('1.0',END)
        
        
