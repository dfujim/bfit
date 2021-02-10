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
        self.win.title('Set deadtime')
        frame = ttk.Frame(self.win, relief='sunken', pad=5)
        
        # icon
        bfit.set_icon(self.win)
        
        # Key bindings
        self.win.bind('<Return>', self.set)        
        self.win.bind('<KP_Enter>', self.set)
        
        # TD mode input ------------------------------------------------------
        frame_entry_slr = ttk.Frame(frame, pad=5)
        
        check_slr = ttk.Checkbutton(frame_entry_slr, 
                text='Calculate and apply deadtime correction for each 20/2h run', 
                variable=self.bfit.deadtime_slr, onvalue=True, offvalue=False, 
                pad=5)
        
        # grid
        check_slr.grid(column=0, row=0)
        
        # TI mode input ------------------------------------------------------
        frame_entry_1f = ttk.Frame(frame, pad=5)
        label_1 = ttk.Label(frame_entry_1f, text="Apply a deadtime correction of ", 
                            pad=5, justify=LEFT)
        label_2 = ttk.Label(frame_entry_1f, text="(s) to 1f/1w/1n runs", pad=5, 
                            justify=LEFT)
        
        self.dt_var = StringVar()
        self.dt_var.set(str(self.bfit.deadtime_1f))
        dt_entry = Entry(frame_entry_1f, textvariable=self.dt_var, width=15,        
                         justify=CENTER)
        
        # grid the input
        label_1.grid(column=0, row=0)
        dt_entry.grid(column=1, row=0)
        label_2.grid(column=2, row=0)
        
        # add buttons
        frame_buttons = ttk.Frame(frame, pad=5)
        
        set_button = ttk.Button(frame_buttons, text='Set', command=self.set)
        close_button = ttk.Button(frame_buttons, text='Cancel', command=self.cancel)
        set_button.grid(column=0, row=0, padx=2)
        close_button.grid(column=1, row=0, padx=2)
            
        # grid frames --------------------------------------------------------
        frame.grid(column=0, row=0)
        frame_entry_slr.grid(column=0, row=1, sticky=W)
        frame_entry_1f.grid(column=0, row=2, sticky=W)
        frame_buttons.grid(column=0, row=3)
        self.logger.debug('Initialization success. Starting mainloop.')
        
    # ====================================================================== #
    def set(self, *args):
        """Set entered values"""
       
        self.bfit.deadtime_1f = float(self.dt_var.get())
        self.logger.info('Setting 1f/1w/1n deadtime to %g', self.bfit.deadtime_1f)
        self.win.destroy()
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
