#!/usr/bin/python3
# Fit and draw BNMR data 
# Derek Fujimoto
# November 2017

from tkinter import *
from tkinter import ttk,filedialog,messagebox
from bdata import bdata
from scipy.optimize import curve_fit

try:
    from mpl_toolkits.mplot3d import Axes3D
except ImportError as errmsg:
    print('No 3D axes drawing available')
    print(errmsg)

import sys,os,datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import webbrowser
import subprocess
import importlib

from bfit.gui.fileviewer_tab import fileviewer
from bfit.gui.fitviewer_tab import fitviewer
from bfit.gui.fetch_files_tab import fetch_files
from bfit.gui.fit_files_tab import fit_files
from bfit.gui.zahersCalculator import zahersCalculator
from bfit.gui.monikasCalculator import monikasCalculator
from bfit.gui.drawstyle_popup import drawstyle_popup

__doc__="""
    BNMR/BNQR data visualization and curve fitting.
    
    Requirements:                       pip3 package name
        python 3.5.2 or higher
        tkinter 8.5 or higher           (python3-tk)
        numpy 1.13.0 or higher          (numpy)
        scipy 1.0.0 or higher           (scipy)
        matplotlib 2.1.0 or higher      (matplotlib)
        pandas 0.21.0 or higher         (pandas)
        
    Packages should be installable using "pip3 install pckg" or 
    "pip3 install --upgrade pckg"
        
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
            data: list of bdata objects for drawing/fitting
            draw_style: draw window types # stack, redraw, new
            root: tkinter root instance
            mainframe: main frame for the object
            routine_mod: module with fitting routines
            
            notebook: contains all tabs for operations:
                fileviewer
                fitviewer
                fetch_files
                fit_files
            
            update_period: update spacing in s. 
            rounding: number of decimal places to round results to in display
    
            
    """
    probe_species = "8Li" # unused
    bnmr_archive_label = "BNMR_ARCHIVE"
    bnqr_archive_label = "BNQR_ARCHIVE"
    update_period = 5
    rounding = 3       # number of decimal places to round results to in display
    
    try: 
        bnmr_data_dir = os.environ[bnmr_archive_label]
        bnqr_data_dir = os.environ[bnqr_archive_label]
    except AttributeError:
        bnmr_data_dir = os.getcwd()
        bnqr_data_dir = os.getcwd()
        
    # ======================================================================= #
    def __init__(self):
        
        # root 
        root = Tk()
        root.title("BFIT - BNMR/BNQR Data Fitting and Visualization")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
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
        menu_file.add_command(label='BNMR Oscillating Field Calculator',\
                command=monikasCalculator)
        menu_file.add_command(label='BNQR Static Field Calculator',\
                command=zahersCalculator)
        menu_file.add_command(label='Export',command=self.do_export)
        menu_file.add_command(label='Exit',command=sys.exit)
        menubar.add_cascade(menu=menu_file, label='File')
        
        # Settings
        menu_settings = Menu(menubar)
        menubar.add_cascade(menu=menu_settings, label='Settings')
        menu_settings_dir = Menu(menu_settings)
        
        # Settings cascade commands
        menu_settings.add_command(label="Set matplotlib defaults",\
                command=self.set_matplotlib)
        menu_settings.add_command(label='Set drawing style',
                command=self.set_draw_style)
        menu_settings.add_command(label='Set fitting routines',
                command=self.set_fit_routines)
        menu_settings.add_cascade(menu=menu_settings_dir,label='Data Directory')
        
        # Settings: data directory
        menu_settings_dir.add_command(label="BNMR",command=self.set_bnmr_dir)
        menu_settings_dir.add_command(label="BNQR",command=self.set_bnqr_dir)
        
        # Draw style
        self.draw_style = StringVar()
        self.draw_style.set("new")
        
        menu_draw = Menu(menubar)
        menubar.add_cascade(menu=menu_draw,label='Redraw Mode')
        menu_draw.add_radiobutton(label="Draw in new window",\
                variable=self.draw_style,value='new',underline=8)
        menu_draw.add_radiobutton(label="Stack in existing window",\
                variable=self.draw_style,value='stack',underline=0)
        menu_draw.add_radiobutton(label="Redraw in existing window",\
                variable=self.draw_style,value='redraw',underline=0)
        
        # Help
        menu_help = Menu(menubar)
        menubar.add_cascade(menu=menu_help, label='Help')
        menu_help.add_command(label='Show help wiki',command=self.help)
        
        # Top Notebook: File Viewer, Fit, Fit Viewer -------------------------
        noteframe = ttk.Frame(mainframe,relief='sunken',pad=5)
        notebook = ttk.Notebook(noteframe)
        file_viewer_tab = ttk.Frame(notebook)
        fetch_files_tab = ttk.Frame(notebook)
        fit_files_tab = ttk.Frame(notebook)
        fit_viewer_tab = ttk.Frame(notebook)
        
        notebook.add(file_viewer_tab,text='File Details')
        notebook.add(fetch_files_tab,text='Fetch Data')
        notebook.add(fit_files_tab,text='Fit Data')
        notebook.add(fit_viewer_tab,text='View Fit Results',state=DISABLED)
        
        # gridding
        notebook.grid(column=0,row=0,sticky=(N,E,W,S))
        noteframe.grid(column=0,row=0,sticky=(N,E,W,S))
        noteframe.columnconfigure(0,weight=1)
        noteframe.rowconfigure(0,weight=1)
        
        # Notetabs
        self.fileviewer = fileviewer(file_viewer_tab,self)
        self.fetch_files = fetch_files(fetch_files_tab,self)
        self.fit_files = fit_files(fit_files_tab,self)
        self.fitviewer = fitviewer(fit_viewer_tab,self)
        
        # set instance variables ---------------------------------------------
        self.root = root
        self.mainframe = mainframe
        self.notebook = notebook
        
        # runloop
        self.root.mainloop()

    # ======================================================================= #
    def __del__(self):
        del self.fileviewer
        del self.fetch_files
        del self.fitviewer
        plt.close('all')
    
    # ======================================================================= #
    def do_export(self):
        """Export selected files to csv format. Calls the appropriate function 
        depending on what tab is selected. """ 
        
        idx = self.notebook.index('current')
        
        if idx == 0:        # data viewer
            self.fileviewer.export()
        elif idx == 1:        # data fetch_files
            self.fetch_files.export()
        elif idx == 2:        # fit viewer
            pass
        else:
            pass
    
    # ======================================================================= #
    def draw(self,data,asym_type,rebin=1,option='',**drawargs):
        """Draw the selected file"""
        
        # Settings
        xlabel_dict={'20':"Time (s)",
                     '2h':"Time (s)",
                     '2e':'Frequency (MHz)',
                     '1f':'Frequency (MHz)',
                     '1n':'Voltage (V)'}
        x_tag={'20':"time_s",
               '2h':"time_s",
               '2e':"time",
               '1f':'freq',
               '1n':'mV'}
        
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
        
        # make new window according to draw style and get axes
        if draw_style.get() == 'new':
            plt.figure()
        elif draw_style.get() == 'redraw':
            plt.clf()
        ax = plt.gca()
        ax.get_xaxis().get_major_formatter().set_useOffset(False)
        
        # get asymmetry: raw scans
        if asym_type == 'r' and data.mode in ['1f','1n']:
            a = data.asym('raw',omit=option)
            x = np.arange(len(a.p[0]))
            idx_p = a.p[0]!=0
            idx_n = a.n[0]!=0
            
            xlabel = 'Bin'
            plt.errorbar(x[idx_p],a.p[0][idx_p],a.p[1][idx_p],
                    label=label+"($+$)",**drawargs)
            plt.errorbar(x[idx_n],a.n[0][idx_n],a.n[1][idx_n],
                    label=label+"($-$)",**drawargs)
        
        # do 2e mode
        elif '2e' in asym_type:
            
            # get asym
            a = data.asym()
        
            # draw
            if asym_type in ["2e_rw_c","2e_rw_h"]:
                
                # make 3D axes
                if type(plt.gcf()) == type(None):   plt.figure()
                ax = plt.gcf().add_subplot(111,projection='3d',
                                           label=str(len(plt.gcf().axes)))
                
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
                if asym_type == "2e_rw_c":
                
                    z = a.raw_c[0].transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label,**drawargs)
                    
                elif asym_type == "2e_rw_h":
                
                    z = a.raw_p[0].transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label+' ($+$)',**drawargs)

                    z = a.raw_n[0].transpose()
                    z = np.hstack(z)
                    ax.plot(x,y,z,label=label+' ($-$)',**drawargs)
                
                # plot elements
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Frequency (MHz)')
                ax.set_zlabel('Asymmetry')
                ax.get_yaxis().get_major_formatter().set_useOffset(False)
                ax.get_xaxis().set_ticks(a.time)
            
            else:
                f = a.freq*1e-6 
                if asym_type == '2e_sl_c':
                    plt.errorbar(f,a.sl_c[0],a.sl_c[1],label=label,
                                 **drawargs)
                elif asym_type == '2e_di_c':
                    plt.errorbar(f,a.dif_c[0],a.dif_c[1],label=label,
                                 **drawargs)
                elif asym_type == '2e_sl_h':
                    plt.errorbar(f,a.sl_p[0],a.sl_p[1],
                                 label=label+' ($+$)',**drawargs)
                    plt.errorbar(f,a.sl_n[0],a.sl_n[1],
                                 label=label+' ($-$)',**drawargs)
                elif asym_type == '2e_di_h':
                    plt.errorbar(f,a.dif_p[0],a.dif_p[1],
                                 label=label+' ($+$)',**drawargs)
                    plt.errorbar(f,a.dif_n[0],a.dif_n[1],
                                 label=label+' ($-$)',**drawargs)
                    
                plt.xlabel(xlabel_dict[data.mode])
                plt.ylabel("Asymmetry")
            
        # get asymmetry: not raw scans, not 2e
        else:
            a = data.asym(omit=option,rebin=rebin)
            x = a[x_tag[data.mode]]
            xlabel = xlabel_dict[data.mode]
            
            # unit conversions
            if data.mode == '1n': x /= 1e3
            if data.mode == '1f': x /= 1e6
            
            # plot split helicities
            if asym_type == 'h':
                plt.errorbar(x,a.p[0],a.p[1],label=label+" ($+$)",**drawargs)
                plt.errorbar(x,a.n[0],a.n[1],label=label+" ($-$)",**drawargs)
                
            # plot comined helicities
            elif asym_type == 'c':
                a = data.asym('c',rebin=rebin,omit=option)
                plt.errorbar(*a,label=label,**drawargs)
                
            # attempting to draw raw scans unlawfully
            elif asym_type == 'r':
                return
                
            # draw alpha diffusion
            elif asym_type == 'ad':
                a = data.asym('adif',rebin=rebin)
                plt.errorbar(*a,label=label,**drawargs)
                plt.ylabel(r'$N_\alpha/N_\beta$')
                
            # draw alpha tagged runs
            elif asym_type in ['at_c','at_h','nat_c','nat_h']:
                
                a = data.asym('atag',rebin=rebin)
                t = a.time_s
                
                if asym_type == 'at_c':
                    plt.errorbar(t,a.c_wiA[0],a.c_wiA[1],
                                 label=label+r" $\alpha$",**drawargs)
                
                elif asym_type == 'nat_c':
                    plt.errorbar(t,a.c_noA[0],a.c_noA[1],
                                 label=label+r" !$\alpha$",**drawargs)
                                 
                elif asym_type == 'at_h':
                    plt.errorbar(t,a.p_wiA[0],a.p_wiA[1],
                                 label=label+r" $\alpha$ ($+$)",**drawargs)
                    plt.errorbar(t,a.n_wiA[0],a.n_wiA[1],
                                 label=label+r" $\alpha$ ($-$)",**drawargs)
                
                elif asym_type == 'nat_h':
                    plt.errorbar(t,a.p_noA[0],a.p_noA[1],
                                 label=label+r" !$\alpha$ ($+$)",**drawargs)
                    plt.errorbar(t,a.n_noA[0],a.n_noA[1],
                                 label=label+r" !$\alpha$ ($-$)",**drawargs)
            # unknown run type
            else:
                raise RuntimeError("Unknown draw style")
                    
        # plot elements
        if data.mode != '2e':
            plt.xlabel(xlabel)
            plt.ylabel("Asymmetry")
        plt.tight_layout()
        plt.legend()
    
    # ======================================================================= #
    def draw_binder(self,*args):
        """
            Switch between various functions of the shift+enter button. 
            Bound to ctrl+enter
        """
        
        idx = self.notebook.index('current')
        
        if idx == 0:        # data viewer
            self.fileviewer.draw()
        elif idx == 1:        # data fetch_files
            self.fetch_files.draw_all()
        elif idx == 2:        # fit viewer
            self.fit_files.draw_param()
        else:
            pass
                 
    # ======================================================================= #
    def export(self,data,filename):
        """Export single data file as csv"""
        
        # settings
        title_dict = {'c':"combined",'p':"positive_helicity",
                        'n':"negative_helicity",'time_s':'time_s',
                        'freq':"freq_Hz",'mV':'voltage_mV'}
                        
        index_list = ['time_s','freq_Hz','voltage_mV'] 
        
        # get asymmetry
        asym = data.asym()
        
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
            pass
    
    # ======================================================================= #
    def help(self):
        """Display help wiki"""
        p = os.path
        webbrowser.open(p.split(p.abspath(p.realpath(__file__)))[0]+'/help.html')
    
    # ======================================================================= #
    def on_closing(self):
        """Excecute this when window is closed: destroy and close all plots."""
        
        plt.close('all')
        self.root.destroy()
    
    # ======================================================================= #
    def return_binder(self,*args):
        """Switch between various functions of the enter button. """
        
        idx = self.notebook.index('current')
        
        if idx == 0:        # data viewer
            self.fileviewer.get_data()
        elif idx == 1:        # data fetch_files
            self.fetch_files.return_binder()
        elif idx == 2:        # fit viewer
            self.fit_files.do_fit()
        else:
            pass
    
    # ======================================================================= #
    def set_bnmr_dir(self): 
        """Set directory location via environment variable BNMR_ARCHIVE."""
        d = filedialog.askdirectory(parent=self.root,mustexist=True, 
                initialdir=self.bnmr_data_dir)
            
        if type(d) == str:
            self.bnmr_data_dir = d
            os.environ[self.bnmr_archive_label] = d
            
    # ======================================================================= #
    def set_bnqr_dir(self): 
        """Set directory location via environment variable BNQR_ARCHIVE."""
        d = filedialog.askdirectory(parent=self.root,mustexist=True, 
                initialdir=self.bnqr_data_dir)
        
        if type(d) == str:
            self.bnqr_data_dir = d
            os.environ[self.bnqr_archive_label] = d
        
    # ======================================================================= #
    def set_fit_routines(self):
        """Set python module for fitting routines"""
        
        d = filedialog.askopenfilename(initialdir = "./",
                title = "Select fitting routine module",
                filetypes = (("python modules","*.py"),
                             ("cython modules","*.pyx"),
                             ("all files","*.*")))
        
        if type(d) == str:
            
            # empty condition
            if d == '':
                return
            
            # get paths
            path = os.path.abspath(d)
            pwd = os.getcwd()
            
            # load the module
            os.chdir(os.path.dirname(path))
            self.routine_mod = importlib.import_module(os.path.splitext(
                                                        os.path.basename(d))[0])
            os.chdir(pwd)
            
            # repopuate fitter
            self.fit_files.fitter = self.routine_mod.fitter()
            self.fit_files.populate()
            
    # ======================================================================= #
    def set_matplotlib(self): 
        """Edit matplotlib settings file, or give info on how to do so."""
        
        # settings
        location = os.environ['HOME']+"/.config/matplotlib/"
        filename = "matplotlibrc"
        weblink = 'http://matplotlib.org/users/customizing.html'+\
                  '#the-matplotlibrc-file'
        
        # check for file existance
        if not os.path.isfile(location+filename):
            value = messagebox.showinfo(parent=self.mainframe,
                    title="Get matplotlibrc",\
                    message="No matplotlibrc file found.",
                    detail="Press ok to see web resource.",
                    type='okcancel')
            
            if value == 'ok':
                webbrowser.open(weblink)
            return
        
        # if file exists, edit
        subprocess.call(['xdg-open',location+filename])
            
    # ======================================================================= #
    def set_check_all(self,x):  
        state = self.fetch_files.check_state.get()
        self.fetch_files.check_state.set(not state)
        self.fetch_files.check_all()
    def set_draw_style(self):       drawstyle_popup(self)
    def set_style_new(self,x):      self.draw_style.set('new')
    def set_style_stack(self,x):    self.draw_style.set('stack')
    def set_style_redraw(self,x):   self.draw_style.set('redraw')
    
# =========================================================================== #
if __name__ == "__main__":
    bfit()

