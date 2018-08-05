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
            data: dictionary of bdata objects, keyed by run number. 
            file_tabs: dictionary of fitinputtab objects, keyed by runnumber 
            fit_function_title: title of fit function to use
            fit_function_title_box: spinbox for fit function names
            groups: group numbers from fetch tab
            n_component: number of fitting components
            runbook: notebook of fit inputs for runs
            runmode: what type of run is this. 
            runmode_label: display run mode 
            
            
            
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
        self.groups = []
        
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
    def populate(self,*args):
        """
            Make tabs for setting fit input parameters. 
        """
        
        # get data
        self.data = self.bfit.fetch_files.data
        
        # get groups 
        dl = self.bfit.fetch_files.data_lines
        self.groups = [dl[k].group.get() for k in dl.keys()]
        
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
        for g in self.groups:
            
            # add to list of groups
            if not g in self.file_tabs.keys():
                self.file_tabs[g] = fitinputtab(self.bfit,self.file_tabs,self.runbook,g)
                    
        # clean up old tabs
        del_list = [k for k in self.file_tabs.keys() if not k in self.groups]
        
        for k in del_list:
            del self.file_tabs[k]
                    
        # add tabs to notebook
        for k in self.file_tabs.keys():
            self.file_tabs[k].create()
            
# =========================================================================== #
# =========================================================================== #
class fitinputtab(object):
    
    n_runs_max = 5      # number of runs before scrollbar appears
    
    # ======================================================================= #
    def __init__(self,bfit,fetch_tabs,parent,group):
        """
            Inputs:
                bfit: top level pointer
                fetch_tabs: list of fitinputtab objects
                fitframe: mainframe for this tab. 
                group: number of data group to fit
                mode: run mode from bdata object
                runlist: list of run numbers to fit
                field
                field_text
                bias
                bias_text
                temperature
                
        """
        
        # initialize
        self.bfit = bfit
        self.parent = parent
        self.group = group
        
        # check state 
        self.check_state = BooleanVar()
        
        # set data mode
        dl = self.bfit.fetch_files.data_lines
        self.mode = dl[list(dl.keys())[0]].mode
        
    # ======================================================================= #
    def create(self):
        """Create graphics for this object"""
        
        fitframe = ttk.Frame(self.parent)
        self.parent.add(fitframe,text='Group %d' % self.group)
        
        # get list of runs with the group number
        dl = self.bfit.fetch_files.data_lines
        self.runlist = [dl[k].run for k in dl.keys() 
                            if dl[k].group.get() == self.group]
        
        # Display run info label 
        ttk.Label(fitframe,text="Run Numbers").grid(column=0,row=0,padx=5)

        # List box for run viewing
        rlist = StringVar(value=tuple(map(str,self.runlist)))
        runbox = Listbox(fitframe,height=min(len(self.runlist),self.n_runs_max),
                         width=10,listvariable=rlist,justify=CENTER)
        runbox.grid(column=0,row=1)
        
        sbar = ttk.Scrollbar(fitframe, orient=VERTICAL, command=runbox.yview)
        runbox.configure(yscrollcommand=sbar.set)
        
        if len(self.runlist) > self.n_runs_max:
            sbar.grid(column=1,row=1,sticky=(N,S))
        else:
            ttk.Label(fitframe,text=" ").grid(column=1,row=1,padx=5)
        
        # Parameter input labels
        ttk.Label(fitframe,text='Parameter').grid(      column=2,row=0,padx=5)
        ttk.Label(fitframe,text='Initial Value').grid(  column=3,row=0,padx=5)
        ttk.Label(fitframe,text='Bounds').grid(         column=4,row=0,padx=5)
        ttk.Label(fitframe,text='Fixed').grid(          column=5,row=0,padx=5)
        
        # save
        self.fitframe = fitframe
        
