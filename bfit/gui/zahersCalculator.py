# Calculate needed current from desired magnetic field. 
# Derek Fujimoto
# December 2017

from tkinter import *
from tkinter import ttk
import numpy as np
import webbrowser

# =========================================================================== #
class zahersCalculator(object):
    
    # ======================================================================= #
    def __init__(self):
        """Draw window for Zaher's calculator"""
        
        # root 
        root = Toplevel()
        root.title("Zaher's Caculator")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # key bindings
        root.bind('<Return>',self.calculate)             
        root.bind('<KP_Enter>',self.calculate)
        
        # variables
        self.field = StringVar()
        self.field.set("")
        self.current = StringVar()
        self.current.set("")
        
        # main frame
        mainframe = ttk.Frame(root,pad=5)
        mainframe.grid(column=0,row=0,sticky=(N,W))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # Entry and other objects
        title_line = ttk.Label(mainframe,   
                text='BNQR Magnetic Static Field -- Current Converter',
                justify=CENTER)
        self.entry_field = ttk.Entry(mainframe,textvariable=self.field,width=10)
        gauss = ttk.Label(mainframe,text='Gauss')
        equals = ttk.Label(mainframe,text='=')
        self.entry_current = ttk.Entry(mainframe,
                textvariable=self.current,width=10)
        amperes = ttk.Label(mainframe,text='Amperes')
        explanation = ttk.Label(mainframe,
                text='Press Enter to convert\n\n'+\
                '(http://bnmr.triumf.ca/?file=HH_Calibration)',
                justify=CENTER)
        
        # Gridding
        title_line.grid(        column=0,row=0,padx=5,pady=5,columnspan=5)
        self.entry_field.grid(  column=0,row=1,padx=5,pady=5)
        gauss.grid(             column=1,row=1,padx=5,pady=5)
        equals.grid(            column=2,row=1,padx=20,pady=5)
        self.entry_current.grid(column=3,row=1,padx=5,pady=5)
        amperes.grid(           column=4,row=1,padx=5,pady=5)
        explanation.grid(       column=0,row=2,padx=5,pady=5,columnspan=5)
        
        # runloop
        self.root = root
        root.mainloop()
        
    # ======================================================================= #
    def calculate(self,*args):
        
        # check focus
        focus_id = str(self.root.focus_get())
        
        # convert field to current
        if focus_id == str(self.entry_field):        
            try:
                field = float(self.field.get()) 
                self.current.set("%.4f" % np.around(field2current(field),4))
            except ValueError:
                self.current.set('Error')
            
        # convert current to field
        elif focus_id == str(self.entry_current):        
            try:
                current = float(self.current.get()) 
                self.field.set("%.4f" % np.around(current2field(current),4))
            except ValueError:
                self.field.set('Error')
            
# ======================================================================= #
def current2field(current):    return current*2.2131+0.175
def field2current(field):      return (field-0.175)/2.2131

