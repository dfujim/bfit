# Model the fit results with a function
# Derek Fujimoto
# August 2019

from tkinter import *
from tkinter import ttk, messagebox
from functools import partial
import logging
import numpy as np
from iminuit import Minuit

from bfit import logger_name
from bfit.gui.template_fit_popup import template_fit_popup
from bfit.backend.raise_window import raise_window
from bfit.fitting.leastsquares import LeastSquares

# ========================================================================== #
class popup_fit_results(template_fit_popup):
    """
        Popup window for modelling the fit results with a function
        
        chi_label:      Label, chisquared output
        fittab:         notebook tab
        reserved_pars:  dict, keys: x,y vals: strings of parameter names
        
        xaxis:          StringVar, x axis drawing/fitting parameter
        yaxis:          StringVar, y axis drawing/fitting parameter
        
    """

    # names of modules the constraints have access to
    modules = {'np':'numpy'}

    window_title = 'Fit the results with a model'
    reserved_pars = ['x','y']

    # ====================================================================== #
    def __init__(self,bfit,input_fn_text='',output_par_text='',output_text='',
                 chi=np.nan,x='',y=''):
        
        super().__init__(bfit, input_fn_text, output_par_text, output_text)
        self.fittab = self.bfit.fit_files
        self.chi = chi
        
        # menus for x and y values
        axis_frame = ttk.Frame(self.left_frame,relief='sunken',pad=5)
        
        ttk.Label(  axis_frame,
                    text='Variable definitions:\n',
                    justify=LEFT).grid(column=0,row=0,columnspan=2,sticky=W)
        ttk.Label(axis_frame,text="x axis:").grid(column=0,row=1)
        ttk.Label(axis_frame,text="y axis:").grid(column=0,row=2)
        ttk.Label(axis_frame,text=' ').grid(column=0,row=3)
        
        self.xaxis = StringVar()
        self.yaxis = StringVar()
        
        if x:   self.xaxis.set(x)
        else:   self.xaxis.set(self.fittab.xaxis.get())
        
        if y:   self.yaxis.set(y)
        else:   self.yaxis.set(self.fittab.yaxis.get())
        
        self.xaxis_combobox = ttk.Combobox(axis_frame,textvariable=self.xaxis,
                                      state='readonly',width=19)
        self.yaxis_combobox = ttk.Combobox(axis_frame,textvariable=self.yaxis,
                                      state='readonly',width=19)
        
        self.xaxis_combobox['values'] = self.fittab.xaxis_combobox['values']
        self.yaxis_combobox['values'] = self.fittab.yaxis_combobox['values']
        
        # module names 
        module_frame = ttk.Frame(self.left_frame,relief='sunken',pad=5)
        s = 'Reserved module names:\n\n'
        
        maxk = max(list(map(len,list(self.modules.keys()))))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk),d) for k,d in self.modules.items()])
        s += '\n'
        modules_label = ttk.Label(module_frame,text=s,justify=LEFT)
        
        # chisquared output
        chi_frame = ttk.Frame(self.left_frame,relief='sunken',pad=5)
        self.chi_label = ttk.Label(chi_frame,
                                    text='ChiSq: %.2f' % np.around(chi,2),
                                    justify=LEFT)
        
        # Text entry
        self.entry_label['text'] = 'Enter a one line equation using "x"'+\
                                 ' to model y(x)'+\
                                 '\nEx: "y = a*x+b"'
                
        # gridding
        modules_label.grid(column=0,row=0)
        self.chi_label.grid(column=0,row=0)
        self.xaxis_combobox.grid(column=1,row=1)
        self.yaxis_combobox.grid(column=1,row=2)
        
        
        axis_frame.grid(column=0,row=0,rowspan=1,sticky=(E,W),padx=1,pady=1)
        module_frame.grid(column=0,row=1,sticky=(E,W),padx=1,pady=1)
        chi_frame.grid(column=0,row=2,sticky=(E,W),padx=1,pady=1,rowspan=2)
        
    # ====================================================================== #
    def _do_fit(self, text):
        
        # get fit data
        xstr = self.xaxis.get()
        ystr = self.yaxis.get()
        
        # Make model
        parnames = self.output_par_text.get('1.0',END).split('\n')[:-1]
        parstr = ','.join(parnames)
        eqn = text[-1].split('=')[-1]
        model = 'lambda x,%s : %s' % (parstr,eqn)
        
        self.logger.info('Fitting model %s for x="%s", y="%s"',model,xstr,ystr)
        
        model = eval(model)
        self.model_fn = model
        npar = len(parnames)
        
        # set up p0, bounds
        p0 = self.new_par['p0'].values
        blo = self.new_par['blo'].values
        bhi = self.new_par['bhi'].values
        
        p0 = list(map(float,p0))
        blo = list(map(float,blo))
        bhi = list(map(float,bhi))
                    
        # get data
        try:
            xvals, xerrs = self.fittab.get_values(xstr)
            yvals, yerrs = self.fittab.get_values(ystr)
        except UnboundLocalError as err:
            self.logger.error('Bad input parameter selection')
            messagebox.showerror("Error",'Select two input parameters')
            raise err
        except (KeyError,AttributeError) as err:
            self.logger.error('Parameter "%s or "%s" not found for fitting',
                              xstr,ystr)
            messagebox.showerror("Error",
                    'Parameter "%s" or "%s" not found' % (xstr,ystr))
            raise err
        
        # split errors    
        if type(xerrs) is tuple: 
            xerrs_l = xerrs[0]
            xerrs_h = xerrs[1]
        else:
            xerrs_l = xerrs
            xerrs_h = xerrs
        
        if type(yerrs) is tuple: 
            yerrs_l = yerrs[0]
            yerrs_h = yerrs[1]
        else:
            yerrs_l = yerrs
            yerrs_h = yerrs
        
        
        xvals = np.asarray(xvals)
        yvals = np.asarray(yvals)
        xerrs_l = np.asarray(xerrs_l)
        yerrs_l = np.asarray(yerrs_l)
        xerrs_h = np.asarray(xerrs_h)
        yerrs_h = np.asarray(yerrs_h)
                        
        # check errors 
        if all(np.isnan(xerrs_l)): xerrs_l = None
        if all(np.isnan(yerrs_l)): yerrs_l = None
        if all(np.isnan(xerrs_h)): xerrs_h = None
        if all(np.isnan(yerrs_h)): yerrs_h = None
        
        # set up least squares
        ls = LeastSquares(model, xvals, yvals, 
                          dy = yerrs_h, 
                          dx = xerrs_h, 
                          dy_low = yerrs_l, 
                          dx_low = xerrs_l)
        
        # minimize
        m = Minuit.from_array_func(ls, p0, name=parnames, errordef=1)
        m.migrad()
        m.hesse()
        m.minos()
        
        # print fitting quality
        print(m.fmin)
        print(m.params)
        print(m.merrors)
        
        # get results
        par = m.np_values()
        
        if npar == 1:
            std_l, std_h = m.np_merrors().T[0]
            std_l = np.array([std_l])
            std_h = np.array([std_h])
        else:
            std_l, std_h = m.np_merrors()
            
        # chisquared
        dof = len(xvals)-npar
        if dof == 0:        chi = np.nan
        else:               chi = ls(par)/dof
        
        # display results 
        self.chi_label['text'] = 'ChiSq: %.2f' % np.around(chi,2)
        self.chi = chi
        
        self.logger.info('Fit model results: %s, Errors-: %s, Errors+: %s',
                        str(par), str(std_l), str(std_h))
        
        self.draw_model(xvals, yvals, (xerrs_l, xerrs_h), (yerrs_l, yerrs_h), par, text)    
        
        return (par, std_l, std_h)
        
    # ======================================================================= #
    def draw_model(self, xvals, yvals, xerrs, yerrs, par, text):
        figstyle = 'param'
        
        # get draw components
        xstr = self.xaxis.get()
        ystr = self.yaxis.get()
        
        self.logger.info('Draw model parameters "%s" vs "%s"',ystr,xstr)
        
        # get fit function and label id
        fn = self.model_fn
        id = self.fittab.par_label.get()

        # get mouseover annotation labels
        mouse_label, _ = self.fittab.get_values('Unique Id')

        # sort by x values, check for empty arrays
        idx = np.argsort(xvals)
        xvals = np.asarray(xvals)[idx]
        yvals = np.asarray(yvals)[idx]
        
        xerrs_l, xerrs_h = xerrs
        yerrs_l, yerrs_h = yerrs
        
        if xerrs_h is not None:     xerrs_h = np.asarray(xerrs_h)[idx]
        if xerrs_l is not None:     xerrs_l = np.asarray(xerrs_l)[idx]
        if yerrs_h is not None:     yerrs_h = np.asarray(yerrs_h)[idx]
        if yerrs_l is not None:     yerrs_l = np.asarray(yerrs_l)[idx]
        
        if xerrs_h is None and xerrs_l is None:     xerrs = None
        else:                                       xerrs = (xerrs_l, xerrs_h)
        if yerrs_h is None and yerrs_l is None:     yerrs = None
        else:                                       yerrs = (yerrs_l, yerrs_h)
        
        mouse_label = np.asarray(mouse_label)[idx]

        # draw data
        self.fittab.plt.errorbar('param', id, xvals, yvals, 
                                 yerr=yerrs,
                                 xerr=xerrs, 
                                 fmt='.', 
                                 annot_label=mouse_label)

        # draw fit
        fitx = np.linspace(min(xvals), max(xvals), self.fittab.n_fitx_pts)
        f = self.fittab.plt.plot(figstyle, id+text[0], fitx, fn(fitx, *par), 
                                 color='k', label=text[0])
        
        # plot elements
        self.fittab.plt.xlabel(figstyle, xstr)
        self.fittab.plt.ylabel(figstyle, ystr)
        self.fittab.plt.tight_layout(figstyle)
        
        raise_window()
