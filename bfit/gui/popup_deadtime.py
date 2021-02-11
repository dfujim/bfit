# Deadtime set and calculate
# Derek Fujimoto
# Feb 2021

from tkinter import *
from tkinter import ttk, messagebox
from bfit import logger_name
import logging, webbrowser, textwrap, datetime
import bdata as bd
import numpy as np
import matplotlib.pyplot as plt

# ========================================================================== #
class popup_deadtime(object):
    """
        Popup window for finding and setting deadtime corrections. 
        
        Attributes: 
        
        bfit:       bfit object
        dt:         Float, calculated deadtime output
        dt_calc:    StringVar for calculated deadtime output
        dt_calc_err:StringVar for calculated deadtime error output
        dt_calc_chi:StringVar for calculated deadtime chi2 output
        dt_over:    StringVar for deadtime override input
        dt_over_chi:StringVar for deadtime override chi2 output
        logger:     logger 
        run:        IntVar, run number of run to fetch
        use_calc:   BooleanVar, if true use calculated dt value
        win:        root Tk object
        year:       IntVar, year of run to fetch
        
    """

    # ====================================================================== #
    def __init__(self, bfit):
        self.bfit = bfit
        self.dt = 0
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
         # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Find and set deadtime')
        frame = ttk.Frame(self.win, relief='sunken', pad=5)
        
        # icon
        bfit.set_icon(self.win)
        
        # Key bindings
        self.win.bind('<Return>', self.find)        
        self.win.bind('<KP_Enter>', self.find)
        self.win.bind('<Shift-Key-Return>', self.draw)        
        self.win.bind('<Shift-Key-KP_Enter>', self.draw)
        
        # Run entry ----------------------------------------------------------
        frame_run = ttk.Frame(frame, pad=5)
        
        label_year = ttk.Label(frame_run, text="Year:", pad=5, justify=LEFT)
        label_run  = ttk.Label(frame_run, text="Run:", pad=5, justify=LEFT)
        
        self.year = IntVar()
        self.run = IntVar()
        self.year.set(self.bfit.get_latest_year())
        self.run.set(40000)
        
        spin_year = Spinbox(frame_run, from_=2000, to=datetime.datetime.today().year, 
                            textvariable=self.year, width=7)
        spin_run = Spinbox(frame_run, from_=0, to=50000, textvariable=self.run, width=7)
        
        button_find = ttk.Button(frame_run, text='Find Deadtime', command=self.find)
        button_draw = ttk.Button(frame_run, text='Draw', command=self.draw)
        
        # grid
        frame_run.grid(column=0, row=0, sticky='new', padx=2, pady=2)
        label_year.grid(column=0, row=1, sticky='nse', padx=2, pady=0)
        label_run.grid(column=0, row=2, sticky='nse', padx=2, pady=0)
        spin_year.grid(column=1, row=1, sticky='nse', padx=2, pady=2)
        spin_run.grid(column=1, row=2, sticky='nse', padx=2, pady=2)
        button_find.grid(column=3, row=1, rowspan=2, sticky='nws', padx=6, pady=2)
        button_draw.grid(column=4, row=1, rowspan=2, sticky='nws', padx=6, pady=2)
        
        frame_run.columnconfigure(2, weight=1)
        
        # calculated deadtime output ----------------------------------------
        frame_calc = ttk.Labelframe(frame, text='Calculated Deadtime', pad=5)
        
        self.dt_calc = StringVar()
        self.dt_calc_err = StringVar()
        self.dt_calc_chi = StringVar()
        
        self.dt_calc.set('')
        self.dt_calc_err.set('')
        self.dt_calc_chi.set('')
        
        label_calc_dt = ttk.Label(frame_calc, textvariable=self.dt_calc, pad=2, 
                                    justify=LEFT)
        label_calc_dt_err = ttk.Label(frame_calc, textvariable=self.dt_calc_err, 
                                    pad=2, justify=LEFT)
        label_calc_dt_chi = ttk.Label(frame_calc, textvariable=self.dt_calc_chi, 
                                    pad=2, justify=LEFT)
        
        label_calc_pm = ttk.Label(frame_calc, text='±', pad=2, justify=LEFT)
        label_calc_s = ttk.Label(frame_calc, text='ns,', pad=2, justify=LEFT)
        label_calc_chi = ttk.Label(frame_calc, text='with a χ2 of', pad=2, justify=LEFT)
        
        # grid
        frame_calc.grid(column=0, row=1, sticky='new', padx=2, pady=2)
        
        c = 0
        label_calc_dt.grid(column=c, row=0, sticky='sew', padx=2); c+= 1
        label_calc_pm.grid(column=c, row=0, sticky='sew', padx=2); c+= 1
        label_calc_dt_err.grid(column=c, row=0, sticky='sew', padx=2); c+= 1
        label_calc_s.grid(column=c, row=0, sticky='sew', padx=0); c+= 1
        label_calc_chi.grid(column=c, row=0, sticky='sew', padx=2); c+= 1
        label_calc_dt_chi.grid(column=c, row=0, sticky='sew', padx=0); c+= 1
                
        # deadtime override --------------------------------------------------
        frame_over = ttk.Labelframe(frame, text='Deadtime Override', pad=5)
        
        self.dt_over = StringVar()
        self.dt_over.set('')
        entry_dt_over = Entry(frame_over, textvariable=self.dt_over, width=10,        
                              justify=CENTER)
        entry_dt_over.bind('<KeyRelease>', self.find_over)
        
        label_over = ttk.Label(frame_over, text='Use instead a deadtime of', pad=2, justify=LEFT)
        label_over_s = ttk.Label(frame_over, text='ns,', pad=2, justify=LEFT)
        
        # frame for line 2
        frame_line2 = ttk.Frame(frame_over)
        
        label_over_chi = ttk.Label(frame_line2, text='which has a χ2 of', pad=2, justify=LEFT)
        
        self.dt_over_chi = StringVar()
        self.dt_over_chi.set('')
        label_over_dt_chi = ttk.Label(frame_line2, textvariable=self.dt_over_chi, pad=2, justify=LEFT)
        
        # grid
        frame_over.grid(column=0, row=2, sticky='new', padx=2, pady=2)
        
        c = 0
        label_over.grid(column=c, row=0, sticky='new', padx=2); c+= 1
        entry_dt_over.grid(column=c, row=0, sticky='new', padx=2); c+= 1
        label_over_s.grid(column=c, row=0, sticky='new', padx=2); c = 0
        frame_line2.grid(column=0, row=1, sticky='new', padx=2)
        label_over_chi.grid(column=0, row=0, sticky='new', padx=2)
        label_over_dt_chi.grid(column=1, row=0, sticky='new', padx=0)
        
        # use calculated value -----------------------------------------------
        self.use_calc = BooleanVar()
        self.use_calc.set(True)
        self.check_calc = ttk.Checkbutton(frame, 
                text='Using calculated value', 
                variable=self.use_calc, onvalue=True, offvalue=False, 
                pad=5, command=self.toggle_check_calc)
        self.check_calc.grid(column=0, row=3, sticky='new', padx=2, pady=2)
            
        # apply correction ---------------------------------------------------
        self.check_corr = ttk.Checkbutton(frame, 
                text='Activate deadtime correction', 
                variable=self.bfit.deadtime_switch, onvalue=True, offvalue=False, 
                pad=5)
        self.check_corr.grid(column=0, row=4, sticky='new', padx=2, pady=0)
            
        # grid frames --------------------------------------------------------
        frame.grid(column=0, row=0)
        self.logger.debug('Initialization success. Starting mainloop.')
        
    # ====================================================================== #
    def draw(self, *args):
        """
            Draw deadtime corrected data
        """
        
        # get data
        try:
            data = bd.bdata(self.run.get(), self.year.get())
        except RuntimeError as msg:
            messagebox.showerror('Bad run input', str(msg))
            raise msg
        
        asym = data.asym('hel')
        asym_dt = data.asym('hel', deadtime=self.bfit.deadtime)
        
        # draw split helicity ------------------------------------------------
        plt.figure()
        plt.errorbar(asym['time_s'], *asym['p'], fmt='.k', zorder=0, 
                     label='Uncorrected')
        plt.errorbar(asym['time_s'], *asym['n'], fmt='.k', zorder=0)
        plt.errorbar(asym_dt['time_s'], *asym_dt['p'], fmt='.r', zorder=5, alpha=0.4, 
                     label='Corrected')
        plt.errorbar(asym_dt['time_s'], *asym_dt['n'], fmt='.r', zorder=5, alpha=0.4 )
        
        # plot elements
        plt.ylabel('Asymmetry')
        plt.xlabel('Time (s)')
        plt.title('Run %d.%d with deadtime correction of %.3f ns' % \
            (self.year.get(), self.run.get(), self.bfit.deadtime*1e9),
            fontsize='small')
        plt.legend(fontsize='small')
        plt.tight_layout()
        
        # draw helicity difference -------------------------------------------
        dasym = 0.5*(asym['p'][0] + asym['n'][0])
        ddasym = 0.5*(asym['p'][1]**2 + asym['n'][1]**2)**0.5
        
        dasym_sub = dasym - np.mean(dasym)
        ddasym_sub = (dasym**2 + np.std(dasym)**2/len(dasym))**2
        
        dasym_dt = 0.5*(asym_dt['p'][0] + asym_dt['n'][0])
        ddasym_dt = 0.5*(asym_dt['p'][1]**2 + asym_dt['n'][1]**2)**0.5
        
        dasym_dt_sub = dasym_dt - np.mean(dasym_dt)
        ddasym_dt_sub = (dasym_dt**2 + np.std(dasym_dt)**2/len(dasym_dt))**2
        
        plt.figure()
        
        plt.errorbar(asym['time_s'], dasym_sub, ddasym_sub, fmt='.k', zorder=0, 
                     label='Uncorrected')
        plt.errorbar(asym_dt['time_s'], dasym_dt_sub, ddasym_dt_sub, fmt='.r', 
                     zorder=5, alpha=0.4, label='Corrected')
        
        plt.axhline(0, ls='-', color='k')
        
        # plot elements
        plt.ylabel(r'$\frac{1}{2}(\mathcal{A}_+ + \mathcal{A}_-)$ - Time Average')
        plt.xlabel('Time (s)')
        plt.title('Run %d.%d with deadtime correction of %.3f ns' % \
            (self.year.get(), self.run.get(), self.bfit.deadtime*1e9),
            fontsize='small')
        plt.legend(fontsize='small')
        plt.tight_layout()
        
        
    # ====================================================================== #
    def find(self, *args):
        """
            Find deadtime of entered run
        """
        
        # get data
        try:
            data = bd.bdata(self.run.get(), self.year.get())
        except RuntimeError as msg:
            messagebox.showerror('Bad run input', str(msg))
            raise msg
        
        # find the correction
        try:
            m = data.get_deadtime(return_minuit=True)
        except RuntimeError as msg:
            messagebox.showerror('Bad run input', str(msg))
            raise msg
        
        dt = m.values[0]
        ddt = m.errors[0]
        chi2 = m.fval
        
        # set the strings
        self.dt = dt
        self.dt_calc.set('%.3f' % dt)
        self.dt_calc_err.set('%.3f' % ddt)
        self.dt_calc_chi.set('%.3f' % chi2)
        
        # set the value
        if self.use_calc.get():
            self.bfit.deadtime = dt*1e-9
        
        # change toggle strings
        self.toggle_check_calc()
        
    # ====================================================================== #
    def find_over(self, *args):
        """
            Find chi2 for override deadtime of entered run
        """
        
        # get data
        try:
            data = bd.bdata(self.run.get(), self.year.get())
        except Exception:
            return
        
        # find the correction
        try:
            dt = float(self.dt_over.get())*1e-9
        except ValueError:
            self.dt_over_chi.set('')
            return
        
        chi2 = data.get_deadtime(dt=dt, search=False)
        
        # set the strings
        self.dt_over_chi.set('%.3f' % chi2)
        
        # set the value
        if not self.use_calc.get():
            self.bfit.deadtime = dt
        
        # change toggle strings
        self.toggle_check_calc()
        
    # ====================================================================== #
    def toggle_check_calc(self, *args):
        """
            Change the deadtime from calculated to override and back
        """
        
        if self.use_calc.get():
            
            try:
                self.bfit.deadtime = self.dt*1e-9
                outstring = 'Using calculated value of %.3f ns' % self.dt
            except ValueError:
                outstring = 'Using calculated value' % self.dt
                
            self.check_calc.config(text=outstring)
            
                
        else:
            try:
                self.bfit.deadtime = float(self.dt_over.get())*1e-9
                outstring = 'Using override value of %s ns' % self.dt_over.get()
            except ValueError:
                outstring = 'Using override value'
        
            self.check_calc.config(text=outstring)
        
