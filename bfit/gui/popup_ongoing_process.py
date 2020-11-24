# Window popup for an ongiong process
# Derek Fujimoto
# Nov 2020

from tkinter import *
from tkinter import ttk

import bfit.backend.colors as colors

class popup_ongoing_process(object):
    """
        bfit:       pointer to bfit object
        process:    multiprocessing.Process
        kill_status:BooleanVar, if true, the process was terminated
    """
    
    
    def __init__(self, bfit, message, process, kill_status):
        """
            root:       TopLevels
            bfit:       pointer to bfit object
            message:    string, summary of process which is ongoing
            process:    multiprocessing.Process
            kill_status:BooleanVar, if true, the process was terminated
        """
        
        # variables
        self.bfit = bfit
        self.process = process
        self.kill_status = kill_status
        self.logger = bfit.logger
        
        # make window
        root = Toplevel(bfit.root)
        root.lift()
        root.resizable(FALSE, FALSE)
        
        # set icon
        self.bfit.set_icon(root)
        
        # set label
        label = ttk.Label(root, 
                      text=message, 
                      justify='center', 
                      pad=0)
        
        # make progress bar
        pbar = ttk.Progressbar(root, orient=HORIZONTAL, 
                               mode='indeterminate', length=200, maximum=20)
        pbar.start()
        
        # make button to cancel the fit
        cancel = ttk.Button(root, 
                      text="Cancel", 
                      command=self.kill,
                      pad=0)

        # grid 
        label.grid(column=0, row=0, padx=15, pady=5)
        pbar.grid(column=0, row=1, padx=15, pady=5)
        cancel.grid(column=0, row=2, padx=15, pady=5)
        
        # set up close window behaviour 
        root.protocol("WM_DELETE_WINDOW", self.kill)
        
        # update
        bfit.root.update_idletasks()
        
        # set window size
        width = root.winfo_reqwidth()
        height = root.winfo_reqheight()
        
        rt_x = bfit.root.winfo_x()
        rt_y = bfit.root.winfo_y()
        rt_w = bfit.root.winfo_width()
        rt_h = bfit.root.winfo_height()
        
        x = rt_x + rt_w/2 - (width/2)
        y = rt_y + rt_h/3 - (width/2)
        
        root.geometry('{}x{}+{}+{}'.format(width, height, int(x), int(y)))
        self.root = root
        
    def destroy(self):
        self.root.destroy()
    
    def update(self):
        self.root.update()
    
    def kill(self):
        """Terminate the processs"""
        
        self.process.terminate()
        self.kill_status.set(True)
        self.logger.info('Fit canceled')    
        print('Fit canceled')    
        
        
