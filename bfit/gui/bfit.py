#!/usr/bin/python3
# Fit and draw BNMR data 
# Derek Fujimoto
# November 2017

from tkinter import *
from tkinter import ttk,filedialog,messagebox
from bdata import bdata
from scipy.optimize import curve_fit

# set MPL backend
import matplotlib as mpl
mpl.use('TkAgg')

try:
    from mpl_toolkits.mplot3d import Axes3D
except ImportError as errmsg:
    print('No 3D axes drawing available')
    print(errmsg)

import sys,os,datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import bdata as bd
import weakref as wref
import webbrowser
import subprocess
import importlib
import logging

from bfit import __version__,logger_name,icon_path
from bfit.gui.tab_fileviewer import fileviewer
from bfit.gui.tab_fetch_files import fetch_files
from bfit.gui.tab_fit_files import fit_files
from bfit.gui.calculator_nqr_B0 import calculator_nqr_B0
from bfit.gui.calculator_nmr_B1 import calculator_nmr_B1
from bfit.gui.popup_drawstyle import popup_drawstyle
from bfit.gui.popup_redraw_period import popup_redraw_period
from bfit.gui.popup_terminal import popup_terminal
from bfit.gui.popup_units import popup_units
from bfit.gui.popup_set_ppm_reference import popup_set_ppm_reference
from bfit.gui.popup_set_histograms import popup_set_histograms
from bfit.backend.PltTracker import PltTracker
from bfit.backend.raise_window import raise_window
import bfit.backend.colors as colors

__doc__="""
    BNMR/BNQR data visualization and curve fitting.
    
    Hotkeys:
    
        General
            Command-------------Effect
            ctrl+n:             set draw mode "new"
            ctrl+s:             set draw mode "stack"
            ctrl+r:             set draw mode "redraw"
    
        File Details
            Command-------------Effect
            return:             fetch file
            ctrl+return:        draw file
            shift+return:       draw file
            ctrl+a:             toggle check all
        Fit 
            Fetch Data
                Command---------Focus-----------------------Effect    
                return:         run/year entry:             fetch
                                SLR rebin:                  set checked
                                bin omit entry (checked):   set checked
                ctrl+return:                                draw file
                shift+return:                               draw file
                
            Fit Data
            
        View Fit Results
    
    Derek Fujimoto
    November 2017
    """

# =========================================================================== #
class bfit(object):
    """
        Build the mainframe and set up the runloop for the tkinter GUI. 
        
        Data Fields:
            asym_dict_keys: asym calc and draw types
            data:           dict of fitdata objects for drawing/fitting, keyed by run #
            draw_style:     draw window types # stack, redraw, new
            draw_components:list of titles for labels, options to export, draw.
            draw_ppm:       BoolVar for drawing as ppm shift
            draw_standardized_res: BoolVar for drawing residuals as standardized
            forced_mode:    StringVar, mode type to force on data file
            freq_unit_conv: conversion rate from original to display units
            freq_units:     string, units to display
            hist_select:    histogram selection for asym calcs (blank for defaults)
            label_default:  StringVar() name of label defaults for fetch
            logger:         logging object 
            logger_name:    string of unique logger name
            ppm_reference:  reference freq in Hz for ppm calulations
            probe_species:  StringVar() name of probe species, bdata.life key.
            mainframe:      main frame for the object
            notebook:       contains all tabs for operations:
                fileviewer
                fetch_files
                fit_files
            plt:            PltTracker for tracking figures
            root:           tkinter root instance
            rounding:       number of decimal places to round results to in display
            routine_mod:    module with fitting routines
            update_period:  int, update spacing in s. 
            use_nbm:        BooleanVar, use NBM in asym calculations
            volt_unit_conv: float, conversion rate from original to display units
            volt_units:     string, units to display
    """
    bnmr_archive_label = "BNMR_ARCHIVE"
    bnqr_archive_label = "BNQR_ARCHIVE"
    update_period = 10  # s
    ppm_reference = 41270000 # Hz
    rounding = 5       # number of decimal places to round results to in display
    hist_select = ''    # histogram selection for asym calculations
    freq_unit_conv = 1.e-6   # conversion rate from original to display units
    volt_unit_conv = 1.e-3   # conversion rate from original to display units
    freq_units = 'MHz'
    volt_units = 'V'
    norm_alph_diff_time = 0.1   # number of seconds to take average over when 
                                # normalizing alpha diffusion runs
    
    asym_dict_keys = {'20':("Combined Helicity","Split Helicity",
                            "Positive Helicity","Negative Helicity",
                            "Matched Helicity","Histograms"),
                      '1f':("Combined Helicity","Split Helicity","Raw Scans",
                            "Positive Helicity","Negative Helicity",
                            "Shifted Split","Shifted Combined","Histograms"),
                      '1n':("Combined Helicity","Split Helicity","Raw Scans",
                            "Positive Helicity","Negative Helicity",
                            "Matched Peak Finding","Histograms"),
                      '1e':("Combined Helicity","Split Helicity","Raw Scans",
                            "Positive Helicity","Negative Helicity",
                            "Histograms"),
                      '1w':("Combined Helicity","Split Helicity","Raw Scans",
                            "Positive Helicity","Negative Helicity",
                            "Shifted Split","Shifted Combined","Histograms"),
                      '2e':("Combined Hel Slopes","Combined Hel Diff","Combined Hel Raw",
                            "Split Hel Slopes","Split Hel Diff","Split Hel Raw",
                            "Split Slopes Shifted","Split Diff Shifted","Split Raw Shifted"),
                      '2h':("Combined Helicity","Split Helicity",
                            "Positive Helicity","Negative Helicity",
                            "Matched Helicity",
                            "Alpha Diffusion", "Alpha Diff Normalized",
                            "Combined Hel (Alpha Tag)","Split Hel (Alpha Tag)",
                            "Combined Hel (!Alpha Tag)","Split Hel (!Alpha Tag)",
                            "Histograms")}
    
    asym_dict = {"Combined Helicity"        :'c',
                 "Split Helicity"           :'h',
                 "Positive Helicity"        :'p',
                 "Negative Helicity"        :'n',
                 "Matched Helicity"         :'hm',
                 "Shifted Split"            :'hs',
                 "Shifted Combined"         :'cs',
                 "Matched Peak Finding"     :'hp',
                 "Raw Scans"                :'r',
                 "Histograms"               :'rhist',
                 "Combined Hel Raw"         :'raw_c',
                 "Combined Hel Slopes"      :'sl_c',
                 "Combined Hel Diff"        :'dif_c',
                 "Split Hel Raw"            :'raw_h',
                 "Split Hel Slopes"         :'sl_h',
                 "Split Hel Diff"           :'dif_h',
                 "Split Raw Shifted"        :'raw_hs',
                 "Split Slopes Shifted"     :'sl_hs',
                 "Split Diff Shifted"       :'dif_hs',
                 "Alpha Diffusion"          :'ad',
                 "Alpha Diff Normalized"    :'adn',
                 "Combined Hel (Alpha Tag)" :"at_c",
                 "Split Hel (Alpha Tag)"    :"at_h",
                 "Combined Hel (!Alpha Tag)":"nat_c",
                 "Split Hel (!Alpha Tag)"   :"nat_h",
                 }
    
    # draw axis labels
    xlabel_dict={'20':"Time (s)",
                 '2h':"Time (s)",
                 '2e':'Frequency (%s)',
                 '1f':'Frequency (%s)',
                 '1w':'x Parameter',
                 '1n':'Voltage (%s)'}
                 
    ylabel_dict={'ad':r'$N_\alpha/N_\beta$', # otherwise, label as Asymmetry
                 'adn':r'$N_\alpha/N_\beta$', 
                 'hs':r'Asym-Asym($\nu_{min}$)',
                 'cs':r'Asym-Asym($\nu_{min}$)',
                 'rhist':'Counts'}
    
    # histogram names for x axis
    x_tag={'20':"time_s",
           '2h':"time_s",
           '2e':"time",
           '1f':'freq',
           '1w':'xpar',
           '1n':'mV'}
    
    data = {}   # for fitdata objects
    
    # define draw componeents in draw_param and labels
    draw_components = ['Temperature (K)','1000/T (1/K)','Impl. Energy (keV)',
                       'Platform Bias (kV)','Run Number','B0 Field (T)', 
                       'Unique Id', 'Sample','RF Level DAC','Chi-Squared',
                       'Run Duration (s)', 'Start Time','Title','Year',
                       'Cryo Lift Set (mm)', 'Cryo Lift Read (mm)',
                       'He Mass Flow','CryoEx Mass Flow', 'Needle Set (turns)',
                       'Needle Read (turns)','Laser Power', 'Target Bias (kV)',
                       'NBM Rate (count/s)', 'Sample Rate (count/s)']
    try: 
        bnmr_data_dir = os.environ[bnmr_archive_label]
        bnqr_data_dir = os.environ[bnqr_archive_label]
    except(AttributeError,KeyError):
        bnmr_data_dir = os.getcwd()
        bnqr_data_dir = os.getcwd()
        
    # ======================================================================= #
    def __init__(self):
        
        # logging
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing ' + '-'*50)
        
        # plot tracker 
        self.plt = PltTracker()
        
        # root 
        root = Tk()
        self.root = root
        root.title("BFIT - BNMR/BNQR Data Fitting and Visualization "+\
                   "(version %s)" % __version__)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # styling
        root.option_add('*tearOff', FALSE)
        root.option_add("*Font", "TkFixedFont")
        root.option_add("*Background",          colors.background)
        root.option_add("*DisabledBackground",  colors.background)
        root.option_add("*ReadonlyBackground",  colors.readonly)
        root.option_add("*Borderwidth", 2)
        
        # don't change all foregrounds or you will break the filedialog windows
        root.option_add("*Menu*Foreground",     colors.foreground)   
        root.option_add("*Spinbox*Foreground",  colors.foreground)
        root.option_add("*Listbox*Foreground",  colors.foreground)
        root.option_add("*Text*Foreground",     colors.foreground)
        
        root.option_add("*Scrollbar.Background",colors.foreground)
        
        ttk_style = ttk.Style()
        ttk_style.configure('.', font='TkFixedFont',
                                   background=colors.background,
                                   foreground=colors.foreground,
                                   arrowcolor=colors.foreground,
                                   borderwidth=2)
                                   
        ttk_style.map('.', background=[('disabled',colors.background)],
                           fieldbackground=[('selected',colors.selected)])
                                         
        ttk_style.configure('TNotebook.Tab', padding=[50,2])
        ttk_style.configure("TNotebook.Tab",background=colors.background)
        ttk_style.map("TNotebook.Tab",background=[("selected",colors.tab)])
        
        ttk_style.configure("TEntry",foreground=colors.foreground,
                                     fieldbackground=colors.fieldbackground)
        
        ttk_style.map("TEntry",foreground     =[('active',  colors.foreground),
                                                ('disabled',colors.disabled)],
                               fieldbackground=[('active',  colors.fieldbackground),
                                                ('disabled',colors.disabled),
                                                ('readonly',colors.readonly)])
                                                                         
        ttk_style.map("TCheckbutton",foreground=[('selected',colors.selected),
                                                 ('disabled',colors.disabled)],
                                     indicatorcolor=[('selected','green3')])
        ttk_style.map('TCombobox', fieldbackground=[('readonly',colors.background)])
        
        ttk_style.configure('TSpinbox', borderwidth=0,background=colors.background)
        ttk_style.map('TSpinbox', borderwidth=[('selected', 1)])
        
        
        # icon
        self.set_icon(root)
            
        # key bindings
        root.bind('<Return>',self.return_binder)             
        root.bind('<KP_Enter>',self.return_binder)
        root.bind('<Control-Key-Return>',self.draw_binder)      
        root.bind('<Control-Key-KP_Enter>',self.draw_binder)
        root.bind('<Shift-Key-Return>',self.draw_binder)
        root.bind('<Shift-Key-KP_Enter>',self.draw_binder)
        
        root.bind('<Control-Key-n>',self.set_style_new)
        root.bind('<Control-Key-s>',self.set_style_stack)
        root.bind('<Control-Key-r>',self.set_style_redraw)
        root.bind('<Control-Key-a>',self.set_check_all)
        
        root.bind('<Control-Key-1>',lambda x: self.set_focus_tab(idn=0))
        root.bind('<Control-Key-2>',lambda x: self.set_focus_tab(idn=1))
        root.bind('<Control-Key-3>',lambda x: self.set_focus_tab(idn=2))
        
        root.bind("<Button-4>",self.scroll_binder) 
        root.bind("<Button-5>",self.scroll_binder)
        
        root.bind("<Control-Key-o>",self.do_load)
        
        # event bindings
        root.protocol("WM_DELETE_WINDOW",self.on_closing)
        
        # drawing styles
        self.style = {'linestyle':'None',
                      'linewidth':mpl.rcParams['lines.linewidth'],
                      'marker':'.',
                      'markersize':mpl.rcParams['lines.markersize'],
                      'capsize':0.,
                      'elinewidth':mpl.rcParams['lines.linewidth'],
                      'alpha':1.,
                      'fillstyle':'full'}
        
        # load default fitting routines
        self.routine_mod = importlib.import_module(
                                                'bfit.fitting.default_routines')
        # main frame
        mainframe = ttk.Frame(root,pad=5)
        mainframe.grid(column=0,row=0,sticky=(N,W,E,S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # Menu bar options ----------------------------------------------------
        root.option_add('*tearOff', FALSE)
        menubar = Menu(root)
        root['menu'] = menubar
        
        # File
        menu_file = Menu(menubar)
        menu_file.add_command(label='Search archive',command=self.search_archive)
        menu_file.add_command(label='NMR B1 Calculator',command=calculator_nmr_B1)
        menu_file.add_command(label='NQR B0 Calculator',command=calculator_nqr_B0)
        menu_file.add_command(label='Run Commands',command=lambda:popup_terminal(wref.proxy(self)))
        menu_file.add_command(label='Export Data',command=self.do_export)
        menu_file.add_command(label='Export Fits',command=self.do_export_fit)
        menu_file.add_command(label='Save State',command=self.do_save)
        menu_file.add_command(label='Load State',command=self.do_load)
        menu_file.add_command(label='Exit',command=sys.exit)
        menubar.add_cascade(menu=menu_file, label='File')
        
        # Settings
        menu_settings = Menu(menubar)
        menubar.add_cascade(menu=menu_settings, label='Settings')
        menu_settings_dir = Menu(menu_settings)
        menu_settings_lab = Menu(menu_settings)
        menu_settings_probe = Menu(menu_settings,selectcolor=colors.selected)
        menu_settings_forcemode = Menu(menu_settings,selectcolor=colors.selected)
        
        # Settings cascade commands
        menu_settings.add_cascade(menu=menu_settings_dir,label='Data directory')
        menu_settings.add_command(label='Drawing style',
                command=self.set_draw_style)
        menu_settings.add_command(label='Fitting routines',
                command=self.set_fit_routines)
        menu_settings.add_cascade(menu=menu_settings_forcemode,label='Force Run Mode')
        menu_settings.add_command(label='Histograms',
                command=self.set_histograms)
        menu_settings.add_cascade(menu=menu_settings_lab,label='Labels default')                
        menu_settings.add_command(label='PPM Reference Frequecy',
                command=self.set_ppm_reference)
        menu_settings.add_cascade(menu=menu_settings_probe,label='Probe Species')
        menu_settings.add_command(label='Redraw period',
                command=self.set_redraw_period)
        menu_settings.add_command(label="System matplotlibrc",
                command=self.set_matplotlib)
        menu_settings.add_command(label="Units",
                command=self.set_units)
        
        # Settings: data directory
        menu_settings_dir.add_command(label="BNMR",command=self.set_bnmr_dir)
        menu_settings_dir.add_command(label="BNQR",command=self.set_bnqr_dir)
        
        # Settings: set label default
        self.label_default = StringVar()
        self.label_default.set('Unique Id')
        for dc in sorted(self.draw_components):
            menu_settings_lab.add_radiobutton(label=dc,
                variable=self.label_default,value=dc,command=self.set_all_labels,
                selectcolor=colors.selected)
        
        # Settings: set probe species
        self.probe_species = StringVar()
        self.probe_species.set('Li8')
        lifekeys = list(bd.life.keys())
        lifekeys.sort()
        for k in lifekeys:
            if 'err' not in k: 
                menu_settings_probe.add_radiobutton(label=k,
                        variable=self.probe_species,
                        value=k,
                        command=self.set_probe_species)
        
        # Settings: force run mode
        self.forced_mode = StringVar()
        self.forced_mode.set('auto')
        menu_settings_forcemode.add_radiobutton(label='auto',
                    variable=self.forced_mode,value='auto')
        for k in self.asym_dict_keys:
            menu_settings_forcemode.add_radiobutton(label=k,
                    variable=self.forced_mode,value=k)
        
        # Draw style
        self.draw_style = StringVar()
        self.draw_style.set("stack")
        self.draw_ppm = BooleanVar()
        self.draw_ppm.set(False)
        self.draw_standardized_res = BooleanVar()
        self.draw_standardized_res.set(False)
        self.use_nbm = BooleanVar()
        self.use_nbm.set(False)
        
        menu_draw = Menu(menubar)
        menubar.add_cascade(menu=menu_draw,label='Draw Mode')
        menu_draw.add_radiobutton(label="Draw in new window",\
                variable=self.draw_style,value='new',underline=8,
                selectcolor=colors.selected)
        menu_draw.add_radiobutton(label="Stack in existing window",\
                variable=self.draw_style,value='stack',underline=0,
                selectcolor=colors.selected)
        menu_draw.add_radiobutton(label="Redraw in existing window",\
                variable=self.draw_style,value='redraw',underline=0,
                selectcolor=colors.selected)
        
        menu_draw.add_separator()
        menu_draw.add_checkbutton(label="Draw 1f as PPM shift",\
                variable=self.draw_ppm,selectcolor=colors.selected)
        menu_draw.add_checkbutton(label="Draw residuals as standardized",\
                variable=self.draw_standardized_res,selectcolor=colors.selected)
        menu_draw.add_checkbutton(label="Use NBM",\
                variable=self.use_nbm,selectcolor=colors.selected)
        
        # Help
        menu_help = Menu(menubar)
        menubar.add_cascade(menu=menu_help, label='Help')
        menu_help.add_command(label='Show help wiki',command=self.help)
        menu_help.add_command(label='Report an issue',command=self.report_issue)
        menu_help.add_command(label='Update bfit',command=self.update_bfit)
        
        # Top Notebook: File Viewer, Fit, Fit Viewer -------------------------
        noteframe = ttk.Frame(mainframe,relief='sunken',pad=5)
        notebook = ttk.Notebook(noteframe)
        file_viewer_tab = ttk.Frame(notebook)
        fetch_files_tab = ttk.Frame(notebook)
        fit_files_tab = ttk.Frame(notebook)
        
        notebook.add(file_viewer_tab,text='Inspect')
        notebook.add(fetch_files_tab,text=' Fetch ')
        notebook.add(fit_files_tab,  text='  Fit  ')
        
        # set drawing styles
        notebook.bind("<<NotebookTabChanged>>",
            lambda event: self.set_tab_change(event.widget.index("current")))
    
        # gridding
        notebook.grid(column=0,row=0,sticky=(N,E,W,S))
        noteframe.grid(column=0,row=0,sticky=(N,E,W,S))
        noteframe.columnconfigure(0,weight=1)
        noteframe.rowconfigure(0,weight=1)
        
        # Notetabs
        self.fileviewer = fileviewer(file_viewer_tab,wref.proxy(self))
        self.fetch_files = fetch_files(fetch_files_tab,wref.proxy(self))
        self.fit_files = fit_files(fit_files_tab,wref.proxy(self))
        
        # set instance variables ---------------------------------------------
        self.mainframe = mainframe
        self.notebook = notebook
        
        # logging 
        self.logger.debug('Initialization success. Starting mainloop.')
        
        # runloop
        self.root.mainloop()
        
    # ======================================================================= #
    def __del__(self):
        if hasattr(self,'fileviewer'):  del self.fileviewer
        if hasattr(self,'fetch_files'): del self.fetch_files
        if hasattr(self,'fitviewer'):   del self.fitviewer
    
        try:
            plt.close('all')
        except ImportError:
            pass
    
    # ======================================================================= #
    def do_export(self):
        """Export selected files to csv format. Calls the appropriate function 
        depending on what tab is selected. """ 
        
        idx = self.notebook.index('current')
        self.logger.debug('Exporting for notebook index %d',idx)
        if idx == 0:        # data viewer
            self.fileviewer.export()
        elif idx == 1:        # data fetch_files
            self.fetch_files.export()
        elif idx == 2:        # fit viewer
            self.fit_files.export()
        else:
            pass
    
    # ======================================================================= #
    def do_export_fit(self): self.fit_files.export_fit()
        
    # ======================================================================= #
    def do_load(self,*args): self.fit_files.load_state()
    
    # ======================================================================= #
    def do_save(self): self.fit_files.save_state()
    
    # ======================================================================= #
    def draw(self,data,asym_type,rebin=1,option='',figstyle='',**drawargs):
        """
            Draw the selected file
            
            data: bdata object
            asym_type: input for asymmetry calculation
            rebin: rebining on asymmetry calculation
            option: options passed to asymmetry calculation
            figstyle: figure style. One of "data", "fit", or "param"
            drawargs: passed to 
        """
        
        self.logger.info('Drawing run %d (%d). mode: %s, rebin: %d, '+\
                     'option: %s, style: %s, %s',
                     data.run,
                     data.year,
                     asym_type,
                     rebin,
                     option,
                     self.draw_style.get(),
                     drawargs)
        
        # get draw setting 
        draw_style = self.draw_style
        plt.ion()
        
        # default label value
        if 'label' not in drawargs.keys():
            label = str(data.run)
        else:
            label = drawargs.pop('label',None)
            
        # set drawing style arguments
        for k in self.style:
            if k not in drawargs.keys():
                drawargs[k] = self.style[k]
        
        
        # make new window
        if draw_style.get() == 'new':
            self.plt.figure(figstyle)
            ax = self.plt.gca(figstyle)
            ax.data_id = []    
            ax.lines_id = []    
        
        # get index of label in run and delete that run
        elif draw_style.get() == 'stack':
            ax = self.plt.gca(figstyle)
        
            # check for id array
            if not hasattr(ax,'data_id'):
                ax.data_id = []
                ax.lines_id = []
            else:
                while data.id in ax.data_id:
                    idx = ax.data_id.index(data.id)
                    idxl = ax.lines_id.index(data.id)
                    
                    # clear lines 
                    del ax.lines[idxl]              
                    
                    # clear errorbar object 
                    if idx < len(ax.collections):   del ax.collections[idx]       
                    
                    # clear errorbar object
                    if idx < len(ax.containers):    del ax.containers[idx]         
                    
                    # clear labels
                    del ax.data_id[idx]
                    del ax.lines_id[idxl]

                # clear excess lines - not fits
                dellist = [i for i,id in enumerate(ax.lines_id) \
                                      if id == 'line']
                dellist = sorted(dellist)[::-1]
                for i in dellist:
                    del ax.lines_id[i]
                    del ax.lines[i]

        # delete all runs
        elif draw_style.get() == 'redraw':
            ax = self.plt.gca(figstyle)

            # check for id array
            if not hasattr(ax,'data_id'):
                ax.data_id = []
                ax.lines_id = []
            else:
                del ax.lines[:]              # clear lines 
                del ax.collections[:]        # clear errorbar object 
                del ax.containers[:]         # clear errorbar object
                del ax.data_id[:]
                del ax.lines_id[:]
                
        ax.get_xaxis().get_major_formatter().set_useOffset(False)
        
        # get asymmetry: raw scans
        if asym_type == 'r' and data.mode in ['1f','1n','1w']:
            a = data.asym('raw',omit=option,hist_select=self.hist_select,
                          nbm=self.use_nbm.get())
            x = np.arange(len(a.p[0]))
            idx_p = a.p[0]!=0
            idx_n = a.n[0]!=0
            
            xlabel = 'Bin'
            self.plt.errorbar(figstyle,x[idx_p],a.p[0][idx_p],a.p[1][idx_p],
                    label=label+"($+$)",**drawargs)
            ax.data_id.append(data.id)
            ax.lines_id.append(data.id)
            self.plt.errorbar(figstyle,x[idx_n],a.n[0][idx_n],a.n[1][idx_n],
                    label=label+"($-$)",**drawargs)
            ax.data_id.append(data.id)
            ax.lines_id.append(data.id)
        
        # do 2e mode
        elif data.mode == '2e':
            
            # get asym
            a = data.asym(hist_select=self.hist_select)
        
            # draw
            if asym_type in ["raw_c","raw_h","raw_hs"]:
                
                # make 3D axes
                if type(self.plt.gcf(figstyle)) == type(None):   
                    self.plt.figure(figstyle)
                ax = self.plt.gcf(figstyle).add_subplot(111,projection='3d',
                                  label=str(len(self.plt.gcf(figstyle).axes)))
                
                # get rid of bad draw options
                try:                del drawargs['capsize']
                except KeyError:    pass
                try:                del drawargs['elinewidth']
                except KeyError:    pass
                
                # for every frequency there is a multiple of times
                x = np.asarray([[t]*len(a.freq) for t in a.time])
                x = np.hstack(x)
                
                # for every time there is a set of frequencies
                y = np.asarray([a.freq for i in range(len(a.raw_c[0][0]))])*1e-6
                y = np.hstack(y)
                    
                # draw combined asym
                if asym_type == "raw_c":
                
                    z = a.raw_c[0].transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label,**drawargs)
                    ax.data_id = data.id
                    ax.lines_id = data.id
                    
                elif asym_type == "raw_h":
                
                    z = a.raw_p[0].transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label+' ($+$)',**drawargs)
                    ax.data_id = data.id
                    ax.lines_id = data.id
                    
                    z = a.raw_n[0].transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label+' ($-$)',**drawargs)
                    ax.data_id = data.id
                    ax.lines_id = data.id
                
                elif asym_type == "raw_hs":
                
                    z = (a.raw_p[0]-a.raw_p[0][0]).transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label+' ($+$)',**drawargs)
                    ax.data_id = data.id
                    ax.lines_id = data.id
                    
                    z = (a.raw_n[0]-a.raw_n[0][0]).transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label+' ($-$)',**drawargs)
                    ax.data_id = data.id
                    ax.lines_id = data.id
                    
                # plot elements
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Frequency (%s)' % self.freq_units)
                
                if asym_type != "raw_hs":
                    ax.set_zlabel('Asymmetry')
                else:
                    ax.set_zlabel(r"Asym-Asym($\nu_{min}$)")
                ax.get_yaxis().get_major_formatter().set_useOffset(False)
                ax.get_xaxis().set_ticks(a.time)
            
            else:
                f = a.freq*self.freq_unit_conv
                if asym_type == 'sl_c':
                    self.plt.errorbar(figstyle,f,a.sl_c[0],a.sl_c[1],label=label,
                                 **drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                elif asym_type == 'dif_c':
                    self.plt.errorbar(figstyle,f,a.dif_c[0],a.dif_c[1],label=label,
                                 **drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                elif asym_type == 'sl_h':
                    self.plt.errorbar(figstyle,f,a.sl_p[0],a.sl_p[1],
                                 label=label+' ($+$)',**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                                 
                    self.plt.errorbar(figstyle,f,a.sl_n[0],a.sl_n[1],
                                 label=label+' ($-$)',**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                elif asym_type == 'dif_h':
                    self.plt.errorbar(figstyle,f,a.dif_p[0],a.dif_p[1],
                                 label=label+' ($+$)',**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                    self.plt.errorbar(figstyle,f,a.dif_n[0],a.dif_n[1],
                                 label=label+' ($-$)',**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                elif asym_type == 'sl_hs':
                    self.plt.errorbar(figstyle,f,a.sl_p[0]-a.sl_p[0][0],a.sl_p[1],
                                 label=label+' ($+$)',**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                                 
                    self.plt.errorbar(figstyle,f,a.sl_n[0]-a.sl_n[0][0],a.sl_n[1],
                                 label=label+' ($-$)',**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                elif asym_type == 'dif_hs':
                    self.plt.errorbar(figstyle,f,a.dif_p[0]-a.dif_p[0][0],a.dif_p[1],
                                 label=label+' ($+$)',**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                    self.plt.errorbar(figstyle,f,a.dif_n[0]-a.dif_n[0][0],a.dif_n[1],
                                 label=label+' ($-$)',**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                    
                self.plt.xlabel(figstyle,self.xlabel_dict[data.mode] % self.freq_units)
                
                if '_hs' in asym_type:
                    self.plt.ylabel(figstyle,r"Asym-Asym($\nu_{min}$)")
                else:
                    self.plt.ylabel(figstyle,"Asymmetry")
            
        # get asymmetry: not raw scans, not 2e
        else:
            a = data.asym(omit=option,rebin=rebin,hist_select=self.hist_select,
                          nbm=self.use_nbm.get())
            x = a[self.x_tag[data.mode]]
            xlabel = self.xlabel_dict[data.mode]
            
            # unit conversions
            if   data.mode == '1n': 
                x *= self.volt_unit_conv
                xlabel = xlabel % self.volt_units
            elif data.mode == '1f': 
                if self.draw_ppm.get():
                    self.logger.info('Drawing as PPM shift with reference %s Hz',
                                     self.ppm_reference)
                    x = 1e6*(x-self.ppm_reference)/self.ppm_reference
                    xlabel = 'Frequency Shift (PPM)'
                else: 
                    x *= self.freq_unit_conv
                    xlabel = xlabel % self.freq_units
                    
            # plot split helicities
            if asym_type == 'h':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
                
                # get average
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                
                # draw
                self.plt.errorbar(figstyle,x[tag_p],ap[tag_p],a.p[1][tag_p],label=label+" ($+$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
                self.plt.errorbar(figstyle,x[tag_n],an[tag_n],a.n[1][tag_n],label=label+" ($-$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
                self.plt.axhline(figstyle,avg,color='k',linestyle='--')
                ax.lines_id.append('line')
                
            # plot positive helicity
            elif asym_type == 'p':
                
                # remove zero asym
                ap = a.p[0]
                tag = ap!=0
                
                # draw
                self.plt.errorbar(figstyle,x[tag],ap[tag],a.p[1][tag],label=label+" ($+$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
            
            # plot negative helicity
            elif asym_type == 'n':
                
                # remove zero asym
                an = a.n[0]
                tag = an!=0
                
                # draw
                self.plt.errorbar(figstyle,x[tag],an[tag],a.n[1][tag],label=label+" ($-$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
            # plot split helicities, shifted by baseline
            elif asym_type == 'hs':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                ap = ap[tag_p]
                an = an[tag_n]
                
                # subtract first value
                loc = np.where(x==min(x))[0][0]
                ap -= ap[loc]
                an -= an[loc]
                
                self.plt.errorbar(figstyle,x[tag_p],ap,a.p[1][tag_p],
                        label=label+" ($+$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
                self.plt.errorbar(figstyle,x[tag_n],an,a.n[1][tag_n],
                        label=label+" ($-$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
            
            # plot split helicities, flipped about the average
            elif asym_type == 'hm':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
            
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                
                self.plt.errorbar(figstyle,x[tag_p],a.p[0][tag_p],a.p[1][tag_p],
                        label=label+" ($+$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
                self.plt.errorbar(figstyle,x[tag_n],2*avg-a.n[0][tag_n],a.n[1][tag_n],
                        label=label+" ($-$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
                self.plt.axhline(figstyle,avg,color='k',linestyle='--')
                ax.lines_id.append('line')
            
            # plot split helicities, flipped about the average, find the largest 
            elif asym_type == 'hp':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                ap = ap[tag_p]
                an = an[tag_n]
                
                # get flipped asymmetries
                if np.mean(an) < avg:
                    an = 2*avg-an
                if np.mean(ap) < avg:
                    ap = 2*avg-ap
                
                # get largest asymmetry
                largest_p = max(ap)
                largest_n = max(an)
                
                if largest_p > largest_n:
                    largest = largest_p
                    vmax = x[np.where(ap==largest)[0][0]]
                else:
                    largest = largest_n
                    vmax = x[np.where(an==largest)[0][0]]
                
                # print
                print('Max asymmetry is %f at V = %f V' % (largest,vmax))
                
                # draw    
                self.plt.errorbar(figstyle,x[tag_p],ap,a.p[1][tag_p],
                                  label=label+" ($+$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
                self.plt.errorbar(figstyle,x[tag_n],an,a.n[1][tag_n],
                                  label=label+" ($-$)",**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
                
                self.plt.axhline(figstyle,largest,color='k',linestyle='--')
                self.plt.axvline(figstyle,vmax,color='k',linestyle='--')
                self.plt.text(figstyle,vmax+0.5,largest+0.0001,'%g V' % vmax)
                ax.lines_id.append('line')
                ax.lines_id.append('line')
                
            # plot comined helicities
            elif asym_type == 'c':
                tag = a.c[0]!=0 # remove zero asym
                self.plt.errorbar(figstyle,x[tag],a.c[0][tag],a.c[1][tag],
                                  label=label,**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
            # plot combined helicities, shifted by baseline
            elif asym_type == 'cs':
                
                # remove zero asym
                ac = a.c[0]
                tag = ac!=0
                ac = ac[tag]
                
                # subtract first value
                x = x[tag]
                loc = np.where(x==min(x))[0][0]
                ac -= ac[loc]
                
                self.plt.errorbar(figstyle,x,ac,a.c[1][tag],label=label,**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                
            # attempting to draw raw scans unlawfully
            elif asym_type == 'r':
                return
                
            # draw alpha diffusion
            elif asym_type == 'ad':
                a = data.asym('adif',rebin=rebin,hist_select=self.hist_select,
                              nbm=self.use_nbm.get())
                self.plt.errorbar(figstyle,*a,label=label,**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                self.plt.ylabel(figstyle,r'$N_\alpha/N_\beta$')
                
            # draw normalized alpha diffusion
            elif asym_type == 'adn':
                
                a = data.asym('adif',rebin=1,hist_select=self.hist_select,
                              nbm=self.use_nbm.get())
                          
                # take mean of first few points
                idx = (a[0]<self.norm_alph_diff_time)*(~np.isnan(a[1]))
                a0 = np.average(a[1][idx],weights=1/a[2][idx]**2)
                
                # normalize
                a = data.asym('adif',rebin=rebin,hist_select=self.hist_select,
                              nbm=self.use_nbm.get())
                a[1] /= a0
                a[2] /= a0
                
                self.plt.errorbar(figstyle,*a,label=label,**drawargs)
                ax.data_id.append(data.id)
                ax.lines_id.append(data.id)
                self.plt.ylabel(figstyle,r'$N_\alpha/N_\beta$ (Normalized by t=0)')
                
            # draw alpha tagged runs
            elif asym_type in ['at_c','at_h','nat_c','nat_h']:
                
                a = data.asym('atag',rebin=rebin,hist_select=self.hist_select,
                              nbm=self.use_nbm.get())
                t = a.time_s
                
                if asym_type == 'at_c':
                    self.plt.errorbar(figstyle,t,a.c_wiA[0],a.c_wiA[1],
                                 label=label+r" $\alpha$",**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                    
                elif asym_type == 'nat_c':
                    self.plt.errorbar(figstyle,t,a.c_noA[0],a.c_noA[1],
                                 label=label+r" !$\alpha$",**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                                 
                elif asym_type == 'at_h':
                    self.plt.errorbar(figstyle,t,a.p_wiA[0],a.p_wiA[1],
                                 label=label+r" $\alpha$ ($+$)",**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                    
                    self.plt.errorbar(figstyle,t,a.n_wiA[0],a.n_wiA[1],
                                 label=label+r" $\alpha$ ($-$)",**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                    
                elif asym_type == 'nat_h':
                    self.plt.errorbar(figstyle,t,a.p_noA[0],a.p_noA[1],
                                 label=label+r" !$\alpha$ ($+$)",**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                    
                    self.plt.errorbar(figstyle,t,a.n_noA[0],a.n_noA[1],
                                 label=label+r" !$\alpha$ ($-$)",**drawargs)
                    ax.data_id.append(data.id)
                    ax.lines_id.append(data.id)
                    
            # draw raw histograms
            elif asym_type == 'rhist':
                
                # make a new figure
                style = draw_style.get()
                
                # get the histograms 
                hist = data.hist
                
                # draw
                keylist = ('F+','F-','B+','B-','L+','R+','L-','R-',
                             'NBMF+','NBMF-','NBMB+','NBMB-','AL0+','AL0-')
                for h in keylist:
                    
                    # get bins
                    try:
                        x = np.arange(len(hist[h].data))
                    except KeyError:
                        continue
                    
                    # check for non-empty histograms, then draw
                    if np.mean(hist[h].data) > 0:                        
                        self.plt.plot(figstyle,x,hist[h].data,label=h)
                        ax.data_id.append(data.id)
                        ax.lines_id.append(data.id)
                        
                self.plt.ylabel(figstyle,self.ylabel_dict[asym_type])
                self.plt.xlabel(figstyle,'Bin')
                            
            # unknown run type
            else:
                raise RuntimeError("Unknown draw style")
                    
        # plot elements
        if data.mode != '2e' and asym_type != 'rhist':
            self.plt.xlabel(figstyle,xlabel)
            
            if asym_type in self.ylabel_dict.keys(): label = self.ylabel_dict[asym_type]
            else:                               label = "Asymmetry"
            if self.use_nbm.get():              label = 'NBM ' + label    
            self.plt.ylabel(figstyle,label)    
            
        self.plt.tight_layout(figstyle)
        self.plt.legend(figstyle)
        
        # bring window to front
        if figstyle != 'periodic':
            raise_window()   
            
        self.logger.debug('Drawing success.')
    
    # ======================================================================= #
    def draw_binder(self,*args):
        """
            Switch between various functions of the shift+enter button. 
            Bound to ctrl+enter
        """
        
        idx = self.notebook.index('current')
        self.logger.debug('Drawing for notebook index %d',idx)
        if idx == 0:        # data viewer
            self.fileviewer.draw(figstyle='data')
        elif idx == 1:        # data fetch_files
            self.fetch_files.draw_all(figstyle='data')
        elif idx == 2:        # fit viewer
            self.fit_files.draw_param()
        else:
            pass
                 
    # ======================================================================= #
    def export(self,data,filename):
        """Export single data file as csv"""
        
        self.logger.info('Exporting single run (%d) as "%s"',data.run,filename)
        
        # settings
        title_dict = {'c':"combined",'p':"positive_helicity",
                        'n':"negative_helicity",'time_s':'time_s',
                        'freq':"freq_Hz",'mV':'voltage_mV','xpar':'x_parameter'}
                        
        index_list = ['time_s','freq_Hz','voltage_mV','x_parameter'] 
        
        # get asymmetry
        asym = data.asym(hist_select=self.hist_select)
        
        # get new keys
        asym_out = {}
        for k in asym.keys():
            if len(asym[k]) == 2:
                asym_out[title_dict[k]] = asym[k][0]
                asym_out[title_dict[k]+"_err"] = asym[k][1]
            else:
                asym_out[title_dict[k]] = asym[k]
        
        # make pandas dataframe
        df = pd.DataFrame.from_dict(asym_out)
        
        # set index
        for i in index_list:
            if i in asym_out.keys():
                df.set_index(i,inplace=True)
                break
        
        # write to file
        try:
            df.to_csv(filename)
        except AttributeError:
            self.logger.exception('Export file write failed')
            pass
    
    # ======================================================================= #
    def get_asym_mode(self,obj):
        """ Get asymmetry calculation type"""
        id_string = obj.asym_type.get()
        return self.asym_dict[id_string]
        
    # ======================================================================= #
    def get_label(self,data):
        """ Get label for plot
            Input: fitdata object. 
        """
        
        # the thing to switch on
        select = self.label_default.get()
        self.logger.debug('Fetching plot label for "%s" (run %d)',select,data.run)
        
        # Data file options
        try:
            if select == 'Temperature (K)':
                label = "%d K" % int(round(data.temperature.mean))
                
            elif select == 'B0 Field (T)':
                if data.field > 0.1:
                    label = "%3.2f T"% np.around(data.field,2)  # field (Tesla)
                else:
                    label = "%3.2f G" % np.round(data.field*1e4)# field (Gauss)
                
            elif select == 'RF Level DAC':
                label = str(int(data.bd.camp.rf_dac.mean))
                
            elif select == 'Platform Bias (kV)':
                label = "%d kV" % int(np.round(data.bias))
                    
            elif select == 'Impl. Energy (keV)':
                label = "%.2f keV" % np.around(data.bd.beam_kev())
                
            elif select == 'Run Duration (s)':
                label = "%d s" % int(data.bd.duration)
                
            elif select == 'Run Number':
                label = str(data.run)
                
            elif select == 'Sample':
                label = data.bd.sample
                
            elif select == 'Start Time':
                label = data.bd.start_date
            
            elif select == 'Title':
                label = data.bd.title
                
            elif select == '1000/T (1/K)':
                label = '%3.3f 1/K' % np.around(1000/data.temperature.mean,2)
                
            elif select == 'Chi-Squared':
                try:
                    label = "%.2f" % np.around(data.chi)
                except(KeyError,AttributeError):
                    label = ""
                
            elif select == 'Year':
                label = '%d' % data.year
            
            elif select == 'Unique Id':
                label = '%d.%d' % (data.year,data.run)
                
            elif 'Cryo Lift Set (mm)' in select:
                label = '%3.2f mm' % np.around(data.bd.camp.clift_set.mean,2)
                
            elif 'Cryo Lift Read (mm)' in select:
                label = '%3.2f mm' % np.around(data.bd.camp.clift_read.mean,2)
                
            elif 'He Mass Flow' in select:
                var = 'mass_read' if data.area == 'BNMR' else 'he_read'
                label = '%3.2f' % np.around(data.bd.camp[var].mean,2)
                
            elif 'CryoEx Mass Flow' in select:
                label = '%3.2f' % np.around(data.bd.camp.cryo_read.mean,2)
                
            elif 'Needle Set (turns)' in select:
                label = '%3.2f turns' % np.around(data.bd.camp.needle_set.mean,2)
                
            elif 'Needle Read (turns)' in select:
                label = '%3.2f turns' % np.around(data.bd.camp.needle_pos.mean,2)
                
            elif 'Laser Power' in select:
                label = '%3.2f' % np.around(data.bd.epics.las_pwr.mean,2)
                
            elif 'Target Bias (kV)' in select:
                label = '%3.2f kV' % np.around(data.bd.epics.target_bias.mean,2)
                
            elif 'NBM Rate (count/s)' in select:
                rate = np.sum([data.hist['NBM'+h].data \
                               for h in ('F+','F-','B-','B+')])/data.duration            
                label = '%3.2f count/s' % np.around(rate,2)
                
            elif 'Sample Rate (count/s)' in select:
                hist = ('F+','F-','B-','B+') if data.area == 'BNMR' \
                                             else ('L+','L-','R-','R+')
                    
                rate = np.sum([data.hist[h].data for h in hist])/data.duration
                label = '%3.2f count/s' % np.around(rate,2)
                
            else:
                label = str(data.run)
        except Exception as err:
            label = '%d (Error)' % data.run
            
        return label
    
    # ======================================================================= #
    def get_latest_year(self):
        """Get the year which has the last data set in it."""
        
        # get the current year
        year = datetime.datetime.now().year
        
        # get paths 
        try:
            nmr_path = os.environ[self.bnmr_archive_label]
            nqr_path = os.environ[self.bnqr_archive_label]
        except KeyError:
            nmr_path = os.path.join(bd._mud_data,'bnmr')
            nqr_path = os.path.join(bd._mud_data,'bnqr')
        
        # functions to check for data (NMR or NQR)
        no_nmr = lambda y: not os.path.isdir(os.path.join(nmr_path,str(y)))
        no_nqr = lambda y: not os.path.isdir(os.path.join(nqr_path,str(y)))
        
        # check data
        while (no_nmr(year) and no_nqr(year)) and year > 0:
            year -= 1
            
        self.logger.debug('Latest year with data: %d (NMR: %s, NQR: %s)',
                          year,not no_nmr(year),not no_nqr(year))
        return year
    
    # ======================================================================= #
    def get_run_key(self,data=None,r=-1,y=-1):
        """For indexing data dictionary"""
        
        if data is not None:
            return '.'.join(map(str,(data.year,data.run)))
        elif r>0 and y>0:
            return '.'.join(map(str,(y,r)))
        else:
            raise RuntimeError('Bad run key input')
    
    # ======================================================================= #
    def help(self):
        """Display help wiki"""
        self.logger.info('Opening help wiki')
        p = os.path
        webbrowser.open(p.split(p.abspath(p.realpath(__file__)))[0]+'/help.html')
    
    # ======================================================================= #
    def on_closing(self):
        """Excecute this when window is closed: destroy and close all plots."""
        self.logger.info('Closing all windows.')
        plt.close('all')
        self.root.destroy()
        self.logger.info('Finished     ' + '-'*50)
    
    # ======================================================================= #
    def report_issue(self):
        """Display github issue page"""
        self.logger.info('Opening github issue page: '+\
                         'https://github.com/dfujim/bfit/issues')
        webbrowser.open('https://github.com/dfujim/bfit/issues')
    
    # ======================================================================= #
    def return_binder(self,*args):
        """Switch between various functions of the enter button. """
        
        idx = self.notebook.index('current')
        self.logger.debug('Calling return key command for notebook index %d',idx)
        if idx == 0:        # data viewer
            self.fileviewer.get_data()
        elif idx == 1:        # data fetch_files
            self.fetch_files.return_binder()
        elif idx == 2:        # fit viewer
            self.fit_files.return_binder()
        else:
            pass
    
    # ======================================================================= #
    def scroll_binder(self,event):
        """
            Switch between various functions of the mousewheel button. 
            Bound to <Button-4> and <Button-5>
        """
        
        idx = self.notebook.index('current')
        
        if idx == 0:        # data viewer
            pass
        elif idx == 1:        # data fetch_files
            self.fetch_files.canvas_scroll(event)
        elif idx == 2:        # fit viewer
            self.fit_files.canvas_scroll(event)
        else:
            pass
               
    # ======================================================================= #
    def search_archive(self):  
        self.logger.info('Opening mud archive musr website')
        webbrowser.open('http://musr.ca/mud/runSel.html',new=1)
        
    # ======================================================================= #
    def set_bnmr_dir(self): 
        """Set directory location via environment variable BNMR_ARCHIVE."""
        self.logger.info('Setting BNMR environment directory')
        d = filedialog.askdirectory(parent=self.root,mustexist=True, 
                initialdir=self.bnmr_data_dir)
            
        if type(d) == str:
            self.bnmr_data_dir = d
            os.environ[self.bnmr_archive_label] = d
            self.logger.debug('Environment variable "%s" set to "%s"',
                              self.bnmr_archive_label,d)
        else:
            self.logger.error('Input was not of type string')
            
    # ======================================================================= #
    def set_bnqr_dir(self): 
        """Set directory location via environment variable BNQR_ARCHIVE."""
        self.logger.info('Setting BNQR environment directory')
        d = filedialog.askdirectory(parent=self.root,mustexist=True, 
                initialdir=self.bnqr_data_dir)
        
        if type(d) == str:
            self.bnqr_data_dir = d
            os.environ[self.bnqr_archive_label] = d
            self.logger.debug('Environment variable "%s" set to "%s"',
                              self.bnqr_archive_label,d)
        else:
            self.logger.error('Input was not of type string')
    
    # ======================================================================= #
    def set_fit_routines(self):
        """Set python module for fitting routines"""
        self.logger.info('Setting fitting backend routine')
        d = filedialog.askopenfilename(initialdir = "./",
                title = "Select fitting routine module",
                filetypes = (("python modules","*.py"),
                             ("cython modules","*.pyx"),
                             ("all files","*.*")))
        
        if type(d) == str:
            
            # empty condition
            if d == '':
                self.logger.error('Input was empty string.')
                return
            
            # get paths
            path = os.path.abspath(d)
            pwd = os.getcwd()
            
            # load the module
            self.logger.info('Loading module...')
            os.chdir(os.path.dirname(path))
            self.routine_mod = importlib.import_module(os.path.splitext(
                                                        os.path.basename(d))[0])
            os.chdir(pwd)
            
            # repopuate fitter
            self.logger.info('Repopulating fitter...')
            self.fit_files.fitter = self.routine_mod.fitter(self.probe_species.get())
            self.fit_files.populate()
        else:
            self.logger.error('Input was not of type string.')    
        self.logger.info('Success.')
        
    # ======================================================================= #
    def set_icon(self,window):
        """Set the icon for new windows"""
        try:
            img = PhotoImage(file=icon_path)
            window.tk.call('wm', 'iconphoto', window._w, img)
        except Exception as err:
            print(err)
        
    # ======================================================================= #
    def set_matplotlib(self): 
        """Edit matplotlib settings file, or give info on how to do so."""
        
        self.logger.info('Attempting to edit matplotlibrc file')
        
        # settings
        location = os.path.join(os.environ['HOME'],'.config','matplotlib')
        filename = "matplotlibrc"
        weblink = 'http://matplotlib.org/users/customizing.html'+\
                  '#the-matplotlibrc-file'
        
        # check for file existance
        if not os.path.isfile(os.path.join(location,filename)):
            self.logger.debug('File not found.')
            value = messagebox.showinfo(parent=self.mainframe,
                    title="Get matplotlibrc",\
                    message="No matplotlibrc file found.",
                    detail="Press ok to see web resource.",
                    type='okcancel')
            
            if value == 'ok':
                webbrowser.open(weblink)
            return
        
        # if file exists, edit
        self.logger.debug('File found. Opening in external program.')
        subprocess.call(['xdg-open',os.path.join(location,filename)])
            
    # ======================================================================= #
    def set_all_labels(self,*a):    self.fetch_files.set_all_labels()
    def set_check_all(self,x):  
        self.logger.info('Checking all files')
        state = self.fetch_files.check_state.get()
        self.fetch_files.check_state.set(not state)
        self.fetch_files.check_all()
    def set_draw_style(self):       popup_drawstyle(wref.proxy(self))
    def set_histograms(self,*a):    popup_set_histograms(wref.proxy(self))
    def set_focus_tab(self,idn,*a): self.notebook.select(idn)
    def set_ppm_reference(self,*a): popup_set_ppm_reference(wref.proxy(self))
    def set_probe_species(self, *a): 
        species = self.probe_species.get()
        self.fit_files.fitter.probe_species = species
        self.fit_files.probe_label['text'] = species
        self.logger.info('Probe species changed to %s',species)
    def set_redraw_period(self,*a): popup_redraw_period(wref.proxy(self))
    def set_units(self,*a):         popup_units(wref.proxy(self))
    def set_style_new(self,x):      
        self.logger.info('Setting draw style to "new"')
        self.draw_style.set('new')
    def set_style_stack(self,x):    
        self.logger.info('Setting draw style to "stack"')
        self.draw_style.set('stack')
    def set_style_redraw(self,x):   
        self.logger.info('Setting draw style to "redraw"')
        self.draw_style.set('redraw')
    def set_tab_change(self,tab_id):
        
        self.logger.debug('Changing to tab %d',tab_id)
        
        # fileviewer
        if tab_id == 0:
            pass
            
        # fetch files
        elif tab_id == 1:
            pass
        
        # fit files
        elif tab_id == 2:
            self.fit_files.populate()
     
    # ======================================================================= #
    def set_asym_calc_mode_box(self,mode,parent,*args):
        """Set asym combobox values. Asymmetry calculation and draw modes."""
        
        self.logger.debug('Setting asym combobox values for mode '+\
                         '"%s"',mode)
    
        # get list of possible run modes
        modes = self.asym_dict_keys[mode]
        
        # prune the list to match only ok files
        if parent == self.fit_files:
            modes2 = modes
            modes = [m for m in modes2 if self.asym_dict[m] in \
                                        self.fit_files.fitter.valid_asym_modes]
            
        # selection: switch if run mode not possible
        if parent.asym_type.get() not in modes:
            parent.asym_type.set(modes[0])
    
        # set list
        parent.entry_asym_type['values'] = modes
        
    # ======================================================================= #
    def update_bfit(self):
        """Check pip for updated version"""
        self.logger.info('Using pip to update')
        subprocess.call([sys.executable, "-m", "pip", "install", "--user", 
                         "--upgrade", 'bfit'])
        print('Done. Restart to implement updates.')
        
# =========================================================================== #
if __name__ == "__main__":
    bfit()

