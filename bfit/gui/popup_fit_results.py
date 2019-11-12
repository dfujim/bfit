# Model the fit results with a function
# Derek Fujimoto
# August 2019

from tkinter import *
from tkinter import ttk, messagebox
from functools import partial
import logging
import numpy as np
from scipy.optimize import curve_fit

from bfit import logger_name
from bfit.gui.template_fit_popup import template_fit_popup
from bfit.backend.raise_window import raise_window

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
        
        super().__init__(bfit,input_fn_text,output_par_text,output_text)
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
    def _do_fit(self,text):
        
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
            
        xvals = np.asarray(xvals)
        yvals = np.asarray(yvals)
        yerrs = np.asarray(yerrs)
                        
        # fit model 
        if all(np.isnan(yerrs)): yerrs = None
        
        par,cov = curve_fit(model,xvals,yvals,sigma=yerrs,absolute_sigma=True,p0=p0)
        std = np.diag(cov)**0.5
        
        if yerrs is None:
            chi = np.sum((model(xvals,*par)-yvals)**2)/(len(xvals)-npar)
        else:
            chi = np.sum(((model(xvals,*par)-yvals)/yerrs)**2)/(len(xvals)-npar)
            
        # display results 
        self.chi_label['text'] = 'ChiSq: %.2f' % np.around(chi,2)
        self.chi = chi
        
        self.logger.info('Fit model results: %s, Errors: %s',str(par),str(std))
        
        self.draw_model(xvals,yvals,yerrs,par)    
        
        return (par,cov)
        
    # ======================================================================= #
    def draw_model(self,xvals,yvals,yerrs,par):
        figstyle = 'param'
        
        # get draw components
        xstr = self.xaxis.get()
        ystr = self.yaxis.get()
        
        self.logger.info('Draw model parameters "%s" vs "%s"',ystr,xstr)
        
        # get fit function
        fn = self.model_fn

        # draw data in new window
        self.bfit.plt.figure('param')
        self.fittab.plt.errorbar('param',xvals,yvals,yerrs,fmt='.')

        # draw
        fitx = np.linspace(min(xvals),max(xvals),self.fittab.n_fitx_pts)
        f = self.fittab.plt.plot(figstyle,fitx,fn(fitx,*par),color='k')
        
        # plot elements
        self.fittab.plt.xlabel(figstyle,xstr)
        self.fittab.plt.ylabel(figstyle,ystr)
        self.fittab.plt.tight_layout(figstyle)
        
        raise_window()
    
