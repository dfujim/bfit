# Terminal access
# Derek Fujimoto
# July 2018

from tkinter import *
from tkinter import ttk
from bfit import logger_name
import logging,os
import matplotlib.pyplot as plt
import numpy as np

# ========================================================================== #
class popup_terminal(object):
    """
        Popup window for python interpreter access. 
    """

    # ====================================================================== #
    def __init__(self,parent):
        self.parent = parent
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(parent.mainframe)
        self.win.title('Interpreter')
        frame = ttk.Frame(self.win,relief='sunken',pad=5)
        
        # Key bindings
        self.win.bind('<Control-Key-Return>',self.do_run)             
        self.win.bind('<Control-Key-KP_Enter>',self.do_run)
        
        # text input 
        self.text = Text(frame,width=80,height=20,state='normal')
        instructions = ttk.Label(frame,text="Press ctrl+enter to execute all.")
        
        # gridding
        frame.grid(row=0,column=0)
        instructions.grid(column=0,row=0,sticky=(E,W),pady=5)
        self.text.grid(row=1,column=0)
        
        
        # grid frame
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def do_run(self,event):
        """
            Run python commands
        """
        
        # remove newline
        if event.keysym == 'Return':
            self.text.delete('insert-1c')
        
        # get full text
        lines = self.text.get("1.0",END)
        self.logger.info('Commands given: "%s"'% ('", "'.join(lines.split('\n')[:-1])))
        exec(lines)
    
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
