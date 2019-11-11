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
from bfit.backend.get_model import get_model
from bfit.gui.template_fit_popup import template_fit_popup
from bfit.backend.raise_window import raise_window

# ========================================================================== #
class popup_fit_results(template_fit_popup):
    """
        Popup window for modelling the fit results with a function
        
        chi_label:      Label, chisquared output
        data:           dict, keys: x,y,dy vals: np arrays of data to fit
        fittab:         notebook tab
        reserved_pars:  dict, keys: x,y vals: strings of parameter names
        
    """

    # names of modules the constraints have access to
    modules = {'np':'numpy'}

    window_title = 'Fit the results with a model'

    # ====================================================================== #
    def __init__(self,bfit,input_fn_text='',output_par_text='',output_text='',
                 chi=np.nan):
        
        super().__init__(bfit,input_fn_text,output_par_text,output_text)
        self.fittab = self.bfit.fit_files
        self.chi = chi
        
        # Keyword parameters
        key_param_frame = ttk.Frame(self.left_frame,relief='sunken',pad=5)
        s = 'Reserved variable names:\n\n'
        self.reserved_pars = {'x':self.fittab.xaxis.get(),
                              'y':self.fittab.yaxis.get()}
        
        maxk = max(list(map(len,list(self.reserved_pars.keys()))))
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk),d) for k,d in self.reserved_pars.items()])
        s += '\n'
        key_param_label = ttk.Label(key_param_frame,text=s,justify=LEFT)
        
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
        
        # get data values
        try:
            xvals, xerrs = self.fittab.get_values(self.reserved_pars['x'])
            yvals, yerrs = self.fittab.get_values(self.reserved_pars['y'])
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
            
        self.data = {'x':xvals,
                     'y':yvals,
                     'dy':yerrs}
        
        # Text entry
        self.entry_label['text'] = 'Enter a one line equation using "x" and "y"'+\
                                 'to model the'+\
                                 '\nselected fit parameters.'+\
                                 '\nEx: "y = a*x+b"'
                
        # gridding
        key_param_label.grid(column=0,row=0)
        modules_label.grid(column=0,row=0)
        self.chi_label.grid(column=0,row=0)
        
        key_param_frame.grid(column=0,row=0,rowspan=1,sticky=(E,W),padx=1,pady=1)
        module_frame.grid(column=0,row=1,sticky=(E,W),padx=1,pady=1)
        chi_frame.grid(column=0,row=2,sticky=(E,W),padx=1,pady=1,rowspan=2)
        
    # ====================================================================== #
    def _do_fit(self,text):
        
        # get fit data
        xstr = self.fittab.xaxis.get()
        ystr = self.fittab.yaxis.get()
        
        # Make model
        parnames = self.output_par_text.get('1.0',END).split('\n')[:-1]
        parstr = ','.join(parnames)
        eqn = text[-1].split('=')[-1]
        model = 'lambda x,%s : %s' % (parstr,eqn)
        
        self.logger.info('Fitting model %s for x="%s", y="%s"',model,xstr,ystr)
        
        model = get_model(model) 
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
        xvals = self.data['x']
        yvals = self.data['y']
        yerrs = self.data['dy']
                    
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
        xstr = self.reserved_pars['x']
        ystr = self.reserved_pars['y']
        
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
    
