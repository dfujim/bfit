# fit_files tab for bfit
# Derek Fujimoto
# Dec 2017

from tkinter import *
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
from functools import partial
from bdata import bdata
import datetime
import matplotlib.pyplot as plt

# =========================================================================== #
# =========================================================================== #
class fit_files(object):
    """
        Data fields:
            runbook: notebook of fit inputs for runs
            fit_function_title: title of fit function to use
            n_component: number of fitting components
            runmode: what type of run is this. 
            runmode_label: display run mode 
            data: dictionary of bdata objects, keyed by run number. 
            file_tabs: dictionary of fitinputtab objects, keyed by runnumber 
            fit_function_title_box: spinbox for fit function names
    """ 
    
    runmode_relabel = {'20':'SLR','1f':'1F','2e':'2e','1n':'Rb Cell Scan'}
    default_fit_functions = {'20':('Exp','Str Exp'),
            '1f':('Lorentzian','Gaussian'),'1n':('Lorentzian','Gaussian')}
    mode = ""

    # ======================================================================= #
    def __init__(self,fit_data_tab,bfit):
        
        # Key binding
        #~ fit_data_tab.bind('<FocusIn>',self.populate)   ################################ REBIND!
        
        # initialize
        self.file_tabs = {}
        self.bfit = bfit
        
        # make top level frames
        top_fit_frame = ttk.Frame(fit_data_tab,pad=5)   # fn select, run mode
        mid_fit_frame = ttk.Frame(fit_data_tab,pad=5)   # notebook
        bot_fit_frame = ttk.Frame(fit_data_tab,pad=5)   # set all
        
        top_fit_frame.grid(column=0,row=0,sticky=(N,W))
        mid_fit_frame.grid(column=0,row=1,sticky=(N,W))
        bot_fit_frame.grid(column=0,row=2,sticky=(N,W))
        
        # TOP FRAME 
        
        # fit function select
        fn_select_frame = ttk.Labelframe(fit_data_tab,text='Fit Function')
        self.fit_function_title = StringVar()
        self.fit_function_title.set("")
        self.fit_function_title_box = ttk.Combobox(fn_select_frame, 
                textvariable=self.fit_function_title,state='readonly')
        
        self.n_component = IntVar()
        self.n_component.set(1)
        n_component_box = Spinbox(fn_select_frame,from_=1,to=20, 
                textvariable=self.n_component,width=5)
        
        # run mode 
        fit_runmode_label_frame = ttk.Labelframe(fit_data_tab,pad=(10,5,10,5),
                text='Run Mode',)
        self.fit_runmode_label = ttk.Label(fit_runmode_label_frame,text="",
                font='bold',justify=CENTER)
        
        # top frame gridding
        fn_select_frame.grid(column=0,row=0)
        self.fit_function_title_box.grid(column=0,row=0)
        ttk.Label(fn_select_frame,text="Number of Components:").grid(column=1,
                row=0,sticky=(E),padx=5,pady=5)
        n_component_box.grid(column=2,row=0,padx=5,pady=5)
        fit_runmode_label_frame.grid(column=1,row=0,sticky=(E,W))
        self.fit_runmode_label.grid(column=0,row=0,sticky=(E,W))
        
        # MID FRAME
        
        self.runbook = ttk.Notebook(mid_fit_frame)
        self.runbook.grid(column=0,row=0)
        
    # ======================================================================= #
    def populate(self):
        """
            Make tabs for setting fit input parameters. 
        """
        
        # get data
        self.data = self.bfit.fetch_files.data
        
        # get run mode by looking at one of the data dictionary keys
        for key_zero in self.data.keys(): break
        
        # if new run mode, reset fit function combobox options
        try:
            if self.mode != self.data[key_zero].mode:
            
                # set run mode 
                self.mode = self.data[key_zero].mode 
                self.fit_runmode_label['text'] = self.runmode_relabel[self.mode]
                
                # set run functions
                fn_titles = self.default_fit_functions[self.mode]
                self.fit_function_title_box['values'] = fn_titles
                self.fit_function_title.set(fn_titles[0])
        except UnboundLocalError:
            self.fit_function_title_box['values'] = ()
            self.fit_function_title.set("")
            self.fit_runmode_label['text'] = ""
            self.mode = ""
        
        # clear old tabs
        for child in self.runbook.winfo_children():
            child.destroy()
        
        # make fitinputtab objects, clean up old tabs
        del_list = []
        for k in self.data.keys():
            
            # add to list of runs
            if not k in self.file_tabs.keys():
                self.file_tabs[k] = fitinputtab(self.bfit,self.file_tabs,
                        self.runbook,self.data[k])
                    
        # clean up old tabs
        data_keys = self.data.keys()
        del_list = []
        for k in self.file_tabs.keys():
            if not k in data_keys:
                del_list.append(k)
        
        for k in del_list:
            del self.file_tabs[k]
                    
        # add tabs to notebook
        for k in self.file_tabs.keys():
            self.file_tabs[k].create()
            
# =========================================================================== #
# =========================================================================== #
class fitinputtab(object):
    
    # ======================================================================= #
    def __init__(self,bfit,fetch_tabs,parent,bd):
        """
            Inputs:
                bfit: top level pointer
                fetch_tabs: list of fitinputtab objects
                fitframe: mainframe for this tab. 
                bd: corresponding bdata object
                mode: run mode from bdata object
                run: run number from bdata object
                field
                field_text
                bias
                bias_text
                temperature
                
        """
        
        # initialize
        self.mode = bd.mode
        self.run = bd.run
        self.parent = parent
        self.year = bd.year
        self.bd = bd
        
        # check state 
        self.check_state = BooleanVar()
        
        # temperature
        try:
            self.temperature = int(np.round(bd.camp.smpl_read_A.mean))
        except AttributeError:
            self.temperature = -1
            
        # field
        try:
            if bd.area == 'BNMR':
                self.field = np.around(bd.camp.b_field.mean,2)
                self.field_text = "%.2f T"%self.field
            else:
                self.field = np.around(bd.camp.hh_current.mean,2)
                self.field_text = "%.2f A"%self.field
        except AttributeError:
            self.field = -1
            self.field_text = ' '*6
        try:
            if bd.area == 'BNMR':
                self.bias = np.around(bd.epics.nmr_bias_p.mean,2)
            else:
                self.bias = np.around(bd.epics.nqr_bias.mean,2)/1000.
                
            if self.bias > 0:
                self.bias_text = "%.2f kV"%self.bias
            else:
                self.bias_text = "% .2f kV"%self.bias
        except AttributeError:
            self.bias = -1
            self.bias_text = ' '*7

    # ======================================================================= #
    def create(self):
        """Create graphics for this object"""
        
        fitframe = ttk.Frame(self.parent)
        self.parent.add(fitframe,text=str(self.run))
        
        # Display run info label 
        ttk.Label(fitframe,text="%d\t%s\t%s\t%3d K" % (self.year,
                self.field_text,self.bias_text,self.temperature)).grid(column=0,
                row=0,columnspan=5)

        # Parameter input labels
        ttk.Label(fitframe,text='Initial Value').grid(column=1,row=1)
        ttk.Label(fitframe,text='Bounds').grid(column=2,row=1)
        ttk.Label(fitframe,text='Fixed').grid(column=3,row=1)
        ttk.Label(fitframe,text='Shared').grid(column=4,row=1)
        
        # save
        self.fitframe = fitframe
