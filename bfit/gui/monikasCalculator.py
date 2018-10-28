# Calculate needed Vpp from desired H1 magnetic field. 
# Derek Fujimoto
# December 2017

from tkinter import *
from tkinter import ttk
import numpy as np
import webbrowser

# =========================================================================== #
class monikasCalculator(object):
    
    # ======================================================================= #
    def __init__(self):
        """Draw window for Monika's calculator"""
        
        # root 
        root = Toplevel()
        root.title("Gerald's Caculator")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # key bindings
        root.bind('<Return>',self.calculate)             
        root.bind('<KP_Enter>',self.calculate)
        
        # variables
        self.field = StringVar()
        self.field.set("")
        self.volt = StringVar()
        self.volt.set("")
        self.nu = StringVar()
        
        self.nu.set('41.27') # MHz
        
        # main frame
        mainframe = ttk.Frame(root,pad=5)
        mainframe.grid(column=0,row=0,sticky=(N,W))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # Entry and other objects
        title_line = ttk.Label(mainframe,   
                text='BNMR Magnetic Oscillating Field -- \n'+\
                     'Antenna Voltage (peak-peak)', 
                     justify=CENTER)
        self.entry_field = ttk.Entry(mainframe,textvariable=self.field,width=10,
                justify=RIGHT)
        gauss = ttk.Label(mainframe,text='Gauss')
        equals = ttk.Label(mainframe,text='=')
        self.entry_voltage = ttk.Entry(mainframe,textvariable=self.volt,
                width=10,justify=RIGHT)
        voltage = ttk.Label(mainframe,text='millivolts')
        explanation = ttk.Label(mainframe,text='Press Enter to convert',
                justify=CENTER)
        
        # frequency input
        freq_frame = ttk.Frame(root,pad=5)
        
        freq1 = ttk.Label(freq_frame,text='Freq:')
        self.entry_freq = ttk.Entry(freq_frame,textvariable=self.nu,width=10,
                                    justify=RIGHT)
        freq2 = ttk.Label(freq_frame,text='MHz')
        
        freq1.grid(column=0,row=0,padx=5)
        self.entry_freq.grid(column=1,row=0,padx=5)
        freq2.grid(column=2,row=0,padx=5)
        
        # Gridding
        title_line.grid(        column=0,row=0,padx=5,pady=5,columnspan=10)
        freq_frame.grid(        column=0,row=1,padx=5,pady=5,columnspan=5)
        self.entry_field.grid(  column=0,row=2,padx=5,pady=5)
        gauss.grid(             column=1,row=2,padx=5,pady=5)
        equals.grid(            column=2,row=2,padx=20,pady=5)
        self.entry_voltage.grid(column=3,row=2,padx=5,pady=5)
        voltage.grid(           column=4,row=2,padx=5,pady=5)
        explanation.grid(       column=0,row=3,padx=5,pady=5,columnspan=5)
        
        # runloop
        self.root = root
        root.mainloop()
        
    # ======================================================================= #
    def calculate(self,*args):
        
        # check focus
        focus_id = str(self.root.focus_get())
        
        # get freqeuency
        nu = float(self.nu.get())
        
        # convert field to voltage
        if focus_id == str(self.entry_field):        
            try:
                field = float(self.field.get()) 
                self.volt.set("%9.6f" % np.around(field/0.0396*nu,6))
            except ValueError:
                self.volt.set('Error')
        
        # convert voltage to field
        elif focus_id == str(self.entry_voltage):        
            try:
                voltage = float(self.volt.get())
                self.field.set("%9.6f" % np.around(voltage*0.0396/nu,6))
            except ValueError:
                self.field.set('Error')
            


