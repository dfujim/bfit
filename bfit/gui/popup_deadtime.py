# Deadtime set and calculate
# Derek Fujimoto
# Feb 2021

from tkinter import *
from tkinter import ttk
from bfit import logger_name
import logging, webbrowser, textwrap

# ========================================================================== #
class popup_deadtime(object):
    """
        Popup window for finding and setting deadtime corrections. 
    """

    # ====================================================================== #
    def __init__(self, bfit):
        self.bfit = bfit
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
         # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Set deadtime for TI mode')
        frame = ttk.Frame(self.win, relief='sunken', pad=5)
        
        # icon
        bfit.set_icon(self.win)
        
        # Key bindings
        self.win.bind('<Return>', self.set)        
        self.win.bind('<KP_Enter>', self.set)
        
        # explanation
        expl_text = "The deadtime may only be calculated from SLR runs, "+\
            "however, if you are reasonably certain of its value, the same "+\
            "correction may be applied to resonance measurements as well. This "+\
            "setting fixes the deadtime correction value for all 1f, 1w, and 1n "+\
            "runs"
        
        expl_text = '\n'.join(textwrap.wrap(expl_text, 50))
        
        ttk.Label(frame, text=expl_text, pad=5, justify=CENTER).grid(column=0, row=0)
        
        # deadtime entry 
        frame_entry = ttk.Frame(frame, pad=5)
        
        self.dt_var = StringVar()
        self.dt_var.set(str(self.bfit.deadtime))
        dt_entry = Entry(frame_entry, textvariable=self.dt_var, width=15, justify=CENTER)
        
        ttk.Label(frame_entry, text='1f/1w/1n Deadtime (s): ', pad=5, justify=LEFT).grid(column=0, row=0)
        dt_entry.grid(column=1, row=0)
        
        # add buttons
        frame_buttons = ttk.Frame(frame, pad=5)
        
        set_button = ttk.Button(frame_buttons, text='Set', command=self.set)
        close_button = ttk.Button(frame_buttons, text='Cancel', command=self.cancel)
        set_button.grid(column=0, row=0, padx=2)
        close_button.grid(column=1, row=0, padx=2)
            
        # grid frame
        frame.grid(column=0, row=0)
        frame_entry.grid(column=0, row=1)
        frame_buttons.grid(column=0, row=2)
        self.logger.debug('Initialization success. Starting mainloop.')
        
    # ====================================================================== #
    def set(self, *args):
        """Set entered values"""
       
        self.bfit.deadtime = float(self.dt_var.get())
        self.logger.info('Setting 1f/1w/1n deadtime to %g', self.bfit.deadtime)
        self.win.destroy()
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
