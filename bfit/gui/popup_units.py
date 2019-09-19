# Drawing style window
# Derek Fujimoto
# July 2018

from tkinter import *
from tkinter import ttk
from bfit import logger_name
import webbrowser
import logging

# ========================================================================== #
class popup_units(object):
    """
        Popup window for setting redraw period. 
    """

    # ====================================================================== #
    def __init__(self,parent):
        self.parent = parent
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(parent.mainframe)
        self.win.title('Set Units')
        frame = ttk.Frame(self.win,relief='sunken',pad=5)
        topframe = ttk.Frame(frame,pad=5)

        # icon
        self.parent.set_icon(self.win)

        # Key bindings
        self.win.bind('<Return>',self.set)             
        self.win.bind('<KP_Enter>',self.set)

        # headers
        l_header = ttk.Label(topframe,text='Conversion',pad=5,justify=LEFT)
        l_header2 = ttk.Label(topframe,text='Unit',pad=5,justify=LEFT)
        l_header3 = ttk.Label(topframe,text='Orignal',pad=5,justify=LEFT)

        # make objects: text entry for frequency
        l_valf = ttk.Label(topframe,text='Frequency:',pad=5,justify=LEFT)
        self.text_valf = StringVar()
        self.text_valf.set(parent.freq_unit_conv)
        entry_valf = ttk.Entry(topframe,textvariable=self.text_valf,width=10,justify=RIGHT)
        l_origf = ttk.Label(topframe,text='(1 = Hz)',pad=5,justify=LEFT)
        
        self.text_strf = StringVar()
        self.text_strf.set(parent.freq_units)
        entry_strf = ttk.Entry(topframe,textvariable=self.text_strf,width=5,justify=RIGHT)
        
        # make objects: text entry for voltage
        l_valv = ttk.Label(topframe,text='Voltage:',pad=5,justify=LEFT)
        self.text_valv = StringVar()
        self.text_valv.set(parent.volt_unit_conv)
        entry_valv = ttk.Entry(topframe,textvariable=self.text_valv,width=10,justify=RIGHT)
        l_origv = ttk.Label(topframe,text='(1 = mV)',pad=5,justify=LEFT)
        
        self.text_strv = StringVar()
        self.text_strv.set(parent.volt_units)
        entry_strv = ttk.Entry(topframe,textvariable=self.text_strv,width=5,justify=RIGHT)
        
        # make objects: buttons
        set_button = ttk.Button(frame,text='Set',command=self.set)
        close_button = ttk.Button(frame,text='Cancel',command=self.cancel)
        
        # grid
        l_header.grid(column=1,row=0)
        l_header2.grid(column=2,row=0)
        l_header3.grid(column=3,row=0)
        l_valf.grid(column=0,row=1)
        entry_valf.grid(column=1,row=1,padx=5)
        entry_strf.grid(column=2,row=1,padx=5)
        l_origf.grid(column=3,row=1,padx=5)
        
        l_valv.grid(column=0,row=2)
        entry_valv.grid(column=1,row=2,padx=5)
        entry_strv.grid(column=2,row=2,padx=5)
        l_origv.grid(column=3,row=2,padx=5)
        
        topframe.grid(column=0,row=0,columnspan=2,pady=10)
        
        set_button.grid(column=0,row=1,pady=10)
        close_button.grid(column=1,row=1,pady=10)
            
        # grid frame
        frame.grid(column=0,row=0)
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def set(self,*args):
        """Set entered values"""        
        self.parent.freq_unit_conv = float(self.text_valf.get())
        self.parent.freq_units = self.text_strf.get()
        self.parent.volt_unit_conv = float(self.text_valv.get())
        self.parent.volt_units = self.text_strv.get()
        self.logger.info('Set freq units %s (%s). Set voltage units %s (%s)',
                            self.parent.freq_unit_conv,
                            self.parent.freq_units,
                            self.parent.volt_unit_conv,
                            self.parent.volt_units,)
        self.win.destroy()
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
