# Set function paramters from gui window
# Derek Fujimoto
# April 2019

from tkinter import *
from tkinter import ttk
from bfit import logger_name
import matplotlib.pyplot as plt
import logging
from bfit.fitting.FunctionPlacer import FunctionPlacer

# ========================================================================== #
class gui_param_popup(object):
    """
        Popup window for graphically finding input parameters. 
        
        logger:     logging variable
        selection:  StringVar, track run selection
        win:        TopLevel window
    """

    # parameter mapping
    parmap = {  '1/T1':'lam',
                'amp':'amp',
                'beta':'beta',
                'baseline':'base',
                'peak':'peak',
                'width':'width',
                'height':'amp',
                'sigma':'width',
                'mean':'peak',
             }

    # ====================================================================== #
    def __init__(self,bfit):
        self.bfit = bfit
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing gui param popup')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Find P0')
        frame = ttk.Frame(self.win,relief='sunken',pad=5)
        
        # Labels
        ttk.Label(frame,text="Select Run").grid(column=0,row=0,sticky=E)
        
        # box for run select
        self.selection = StringVar()
        select_box = ttk.Combobox(frame,textvariable=self.selection,
                                  state='readonly')
        select_box.bind('<<ComboboxSelected>>',self.run)
        
        # get run list
        runlist = list(self.bfit.fit_files.fit_lines.keys())
        runlist.sort()
        # ~ runlist = ['('+r.split('.')[0]+') '+r.split('.')[1] for r in runlist]
        select_box['values'] = runlist
        
        # gridding
        frame.grid(column=0,row=1,sticky=(N,W,E,S))
        select_box.grid(column=0,row=1,sticky=E)
                
    # ====================================================================== #
    def run(self,*args):
        """Main run function"""
        
        # get run selection 
        run_id = self.selection.get()
        self.logger.info('Running P0 GUI finder on run %s',run_id)
        
        # get data
        data = self.bfit.data[run_id]
        mode = data.mode
        
        # mode switching
        if mode in ('20','2h'): mode = 2
        elif mode in ('1f',):   mode = 1
        else:
            self.logger.warning('P0 Finder not configured for run mode %s',mode)
            print('P0 Finder not configured for run mode %s'%mode)
        
        # make new window 
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        # draw data
        omit = data.omit.get()
        if omit == self.bfit.fetch_files.bin_remove_starter_line:
            omit = ''
        x,a,da = data.asym('c',rebin=data.rebin.get(),omit=omit)
        ax.errorbar(x,a,da,fmt='.')
        
        # plot elements
        plt.ylabel('Asymmetry')
        if mode == 2:     plt.xlabel('Time (s)')
        elif mode == 1:   plt.xlabel('Frequency (MHz)')
        plt.tight_layout()
        
        fig.show()
        
        # get parameters list and run finder 
        fit_tab = self.bfit.fit_files
        fitter = fit_tab.fitter
        n_components = fit_tab.n_component.get()
        fname = fit_tab.fit_function_title.get()
        parnames = fitter.gen_param_names(fn_name=fname,
                                                  ncomp=n_components)
        parentry = self.bfit.fit_files.fit_lines[run_id].parentry
        p0 = {self.parmap[k]:parentry[k]['p0'][0] for k in parnames}
        
        # get fitting function 
        if mode == 1:
            f1 = fitter.get_fn(fname,1)
            fn = lambda x,peak,width,amp,base : f1(x,peak,width,amp,base)
                
        elif mode == 2:
            f1 = fit_tab.fitter.get_fn(fname,1)
            if 'beta' in parnames:
                fn = lambda x,lam,amp,beta,base : f1(x,lam,amp,beta,base)
            else:
                fn = lambda x,lam,amp,base : f1(x,lam,amp,base)
                
        # start function placement
        fplace = FunctionPlacer(fig,data,fn,p0)
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()









