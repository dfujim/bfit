# Model the fit results with a function
# Derek Fujimoto
# Nov 2019


from tkinter import *
from tkinter import ttk
from functools import partial

import logging, re, os, warnings
import numpy as np
import pandas as pd
import bdata as bd
import weakref as wref

from bfit import logger_name
from bfit.backend.entry_color_set import on_focusout, on_entry_click
from bfit.backend.raise_window import raise_window
import bfit.backend.colors as colors

from bfit.fitting.fit_bdata import fit_bdata
from bfit.backend.ParameterFunction import ParameterFunction as ParFnGenerator

# ========================================================================== #
class popup_add_param(object):
    """
        Popup window for adding parameters for fitting or drawing
        
        bfit
        fittab
        logger
        
        input_fn_text       string: input lines
        
        new_par:            dict: {parname, string: par equation}
        set_par:            dict: {parname, fn handle: lambda : return new_par}
        parnames:           list, function inputs
        reserved_pars:      dict, define values in bdata that can be accessed
        win:                Toplevel
    """

    # names of modules the constraints have access to
    modules = {'np':'numpy'}
    
    window_title = 'Add parameter for fitting or drawing'
    
    # ====================================================================== #
    def __init__(self, bfit, input_fn_text=''):
        
        self.bfit = bfit
        self.fittab = bfit.fit_files
        
        self.input_fn_text = input_fn_text
        self.set_par = {}
        self.new_par = {}
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title(self.window_title)
        frame = ttk.Frame(self.win, relief='sunken', pad=5)
        left_frame = ttk.Frame(frame)
        right_frame = ttk.Frame(frame)

        # set icon
        try:
            img = PhotoImage(file=os.path.dirname(__file__)+'/../images/icon.gif')
            self.win.tk.call('wm', 'iconphoto', self.win._w, img)
        except Exception as err:
            print(err)

        # Key bindings
        self.win.bind('<Control-Key-Return>', self.do_add)
        self.win.bind('<Control-Key-KP_Enter>', self.do_add)
        
        # Text entry
        entry_frame = ttk.Frame(right_frame, relief='sunken', pad=5)
        self.entry_label = ttk.Label(entry_frame, justify=LEFT, text='')
        self.entry = Text(entry_frame, width=60, height=13, state='normal')
        self.entry.bind('<KeyRelease>', self.get_input)
        scrollb = Scrollbar(entry_frame, command=self.entry.yview)
        self.entry['yscrollcommand'] = scrollb.set
        
        # Insert default text
        self.entry.insert('1.0', self.input_fn_text.strip())
        
        # add button 
        add_button = ttk.Button(right_frame, text='Set Parameters', command=self.do_add)
        
        # gridding
        self.entry_label.grid(column=0, row=0, sticky=W)
        self.entry.grid(column=0, row=1)
        
        # grid to frame
        frame.grid(column=0, row=0)
        left_frame.grid(column=0, row=0, sticky=(N, S))
        right_frame.grid(column=1, row=0, sticky=(N, S))
        
        entry_frame.grid(column=0, row=0, sticky=(N, E, W), padx=1, pady=1)
        add_button.grid(column=0, row=1, sticky=(N, E, W, S), padx=20, pady=20)
        right_frame.rowconfigure(1, weight=1)
        
        # initialize 
        self.left_frame = left_frame
        
        # Keyword parameters
        key_param_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        s = 'Reserved variable names:\n\n'
        self.reserved_pars = ParFnGenerator.keyvars
        
        keys = list(self.reserved_pars.keys())
        descr = [self.reserved_pars[k] for k in self.reserved_pars]
        maxk = max(list(map(len, keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk), d) for k, d in zip(keys, descr)])
        s += '\n'
        key_param_label = ttk.Label(key_param_frame, text=s, justify=LEFT)
        
        # fit parameter names 
        fit_param_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        s = 'Reserved parameter names:\n\n'
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
        self.entry_label['text'] = 'Enter one parameter equation per line.'+\
                '\nLHS must use only reserved words, constants, or functions'+\
                '\nfrom the reserved modules in the parameter definition.'+\
                '\nEx: "mypar = 1/(1_T1*TEMP)"'+\
                '\n\nAccepts LaTeX input for the new parameter.'+\
                '\nEx: "$\eta_\mathrm{f}$ (Tesla) = B0 * np.exp(-amp**2)"' +\
                '\n\nValues taken as shown in fit results, with no unit scaling.'
                
        # gridding
        key_param_label.grid(column=0, row=0)
        fit_param_label.grid(column=0, row=0)
        modules_label.grid(column=0, row=0)
        
        key_param_frame.grid(column=0, row=0, rowspan=1, sticky=(E, W), padx=1, pady=1)
        module_frame.grid(column=0, row=1, sticky=(E, W), padx=1, pady=1, rowspan=2)
        fit_param_frame.grid(column=0, row=3, sticky=(E, W, N, S), padx=1, pady=1)
        
        self.logger.debug('Initialization success. Starting mainloop.')
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
        
    # ====================================================================== #
    def do_add(self, *args):
        """
            Add the parameter and the corresponding function
        """
        # reset draw comp
        self.bfit.fit_files.draw_components = list(self.bfit.draw_components)
        
        # set the parameters
        self.set_par = {}
        try:
            self.set_par = {p: ParFnGenerator(p, e, self.parnames, self.bfit) \
                        for p, e in self.new_par.items()}
        except SyntaxError: # on empty set
            pass
        
        # update the lists
        self.bfit.fit_files.populate_param()
        
    # ====================================================================== #
    def do_parse(self, *args):
        """
            Detect new global variables
            returns split lines, new parameter names 
        """
        
        # clean input
        text = self.input_fn_text.split('\n')
        text = [t.strip() for t in text if '=' in t]
        
        # check for no input
        if not text:
            self.new_par = {}
            return
        
        # get equations and defined variables
        defined = [t.split('=')[0].strip() for t in text]
        eqn = [t.split('=')[1].strip() for t in text]
        
        # set fields
        self.new_par = {k:e for k,e in zip(defined, eqn)}
        
        # save input
        self.input_fn_text = '\n'.join(text)
        
        # logging
        self.logger.info('Parse found parameters %s', self.new_par)
    
    # ====================================================================== #
    def get_input(self, *args):
        """Get input from text box."""
        self.input_fn_text = self.entry.get('1.0', END)
        self.do_parse()
        
    # ====================================================================== #
    def yview(self, *args):
        """
            Scrollbar for all output text fields
        """
        self.output_par_text.yview(*args)
        for k in self.output_text:
            self.output_text[k].yview(*args)

    
