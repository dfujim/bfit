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
from bfit.backend.entry_color_set import on_focusout,on_entry_click
from bfit.backend.get_model import get_model
import bfit.backend.colors as colors
from bfit.backend.raise_window import raise_window

# ========================================================================== #
class popup_fit_results(object):
    """
        Popup window for modelling the fit results with a function
        
        bfit
        fittab
        logger
        
        model_chi_label:    Label, chisquared output
        model_fn:           Funtion handle, fit model for pars, created on fit
        model_p0:           Initial parameters for model fitting
        model_entry:        Entry: model function
        model_results:      Tuple, (par,std) for model fit results
        model_results_fn:   StringVar, fit function to model results
        model_results_par:  StringVar, parameter list of model_results fn
        model_results_text: Text, output model results
        model_errors_text:  Text, output model result errors
        modelp0_entry:      Entry: model p0 list
        modelpar_entry:     Entry: model parameter list
            
        win:                Toplevel
        
    """

    # ====================================================================== #
    def __init__(self,bfit,par_str='a,b',fn_str='a*x+b',p0_str='1,1',
                 result_str='',error_str=''):
        self.bfit = bfit
        self.fittab = bfit.fit_files
        
        self.par_str = par_str
        self.fn_str = fn_str
        self.p0_str = p0_str
        self.result_str = result_str
        self.error_str = error_str
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Model the Fit Results')
        fit_fitresults_frame = ttk.Frame(self.win,relief='sunken',pad=5)
        
        # icon
        self.bfit.set_icon(self.win)

        # Key bindings
        self.win.bind('<Return>',self.do_fit_model)             
        self.win.bind('<KP_Enter>',self.do_fit_model)
        
        self.model_results_fn = StringVar()
        self.model_results_par = StringVar()
        self.model_p0 = StringVar()
        
        # entry
        model_entry_frame = Frame(fit_fitresults_frame)
        self.modelpar_entry = ttk.Entry(model_entry_frame,
                                  textvariable=self.model_results_par,width=6)
        
        self.model_entry = ttk.Entry(model_entry_frame,
                                     textvariable=self.model_results_fn,width=26)
        
        self.modelp0_entry = ttk.Entry(model_entry_frame,
                                  textvariable=self.model_p0,width=26)
                                     
        # entry defaults (parameters)
        self.modelpar_entry.insert(0,self.par_str)
        entry_parfn = partial(on_entry_click,text=self.par_str,entry=self.modelpar_entry)
        on_focusout_parfn = partial(on_focusout,text=self.par_str,entry=self.modelpar_entry)
        self.modelpar_entry.bind('<FocusIn>', entry_parfn)
        self.modelpar_entry.bind('<FocusOut>', on_focusout_parfn)
        self.modelpar_entry.config(foreground=colors.entry_grey)
       
        # entry defaults (function)
        self.model_entry.insert(0,self.fn_str)
        entry_fnfn = partial(on_entry_click,text=self.fn_str,entry=self.model_entry)
        on_focusout_fnfn = partial(on_focusout,text=self.fn_str,entry=self.model_entry)
        self.model_entry.bind('<FocusIn>', entry_fnfn)
        self.model_entry.bind('<FocusOut>', on_focusout_fnfn)
        self.model_entry.config(foreground=colors.entry_grey)
       
        # entry defaults (p0)
        self.modelp0_entry.insert(0,self.p0_str)
        entry_fnp0 = partial(on_entry_click,text=self.p0_str,entry=self.modelp0_entry)
        on_focusout_fnp0 = partial(on_focusout,text=self.p0_str,entry=self.modelp0_entry)
        self.modelp0_entry.bind('<FocusIn>', entry_fnp0)
        self.modelp0_entry.bind('<FocusOut>', on_focusout_fnp0)
        self.modelp0_entry.config(foreground=colors.entry_grey)
       
        # buttons
        model_fit_button = ttk.Button(fit_fitresults_frame,text='Fit',command=self.do_fit_model)
        
        # chisq
        self.model_chi_label = ttk.Label(fit_fitresults_frame,text='',justify=LEFT)
        
        # text for output
        self.model_results_text = Text(fit_fitresults_frame,width=17,height=8,state='normal')
        self.model_errors_text = Text(fit_fitresults_frame,width=17,height=8,state='normal')
        
        self.model_results_text.insert('1.0',self.result_str)
        self.model_errors_text.insert('1.0',self.error_str)
        
        model_entry_frame.grid(column=0,row=0,columnspan=2,sticky=W,pady=2)
        
        ttk.Label(model_entry_frame,text="Param").grid(column=0,row=0,sticky=(N,W))
        ttk.Label(model_entry_frame,text="Model").grid(column=2,row=0,sticky=(N,W))
        self.modelpar_entry.grid(column=0,row=1,padx=2,pady=1,sticky=(N,W))
        ttk.Label(model_entry_frame,text=":").grid(column=1,row=1,sticky=(N,W))
        self.model_entry.grid(column=2,row=1,padx=2,pady=1,sticky=(N,W))
        ttk.Label(model_entry_frame,text="P0").grid(column=0,row=2,sticky=(E))
        ttk.Label(model_entry_frame,text=":").grid(column=1,row=2,sticky=(N,W))
        self.modelp0_entry.grid(column=2,row=2,padx=2,pady=1,sticky=(N,W))
        
        model_fit_button.grid(column=0,row=2,padx=2,pady=2)
        self.model_chi_label.grid(column=1,row=2,padx=2,pady=2)
        
        ttk.Label(fit_fitresults_frame,text="Results").grid(column=0,row=3,pady=2,sticky=N)
        ttk.Label(fit_fitresults_frame,text="Errors").grid(column=1,row=3,pady=2,sticky=N)
        
        self.model_results_text.grid(column=0,row=4,padx=2)
        self.model_errors_text.grid(column=1,row=4,padx=2)
                
        # grid frame
        fit_fitresults_frame.grid(column=0,row=0)
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
    
    # ====================================================================== #
    def do_fit_model(self,*args):
        
        # get fit data
        xstr = self.fittab.xaxis.get()
        ystr = self.fittab.yaxis.get()
        
        # Make model 
        self.par_str = self.model_results_par.get()
        parstr = self.par_str
        parlst = parstr.split(',')
        npar = len(parlst)
        
        if parstr[-1] == ',': parstr = parstr[:-1]
        self.fn_str = self.model_results_fn.get()
        model = 'lambda x,%s : %s' % (parstr,self.fn_str)
        
        self.logger.info('Fitting model %s for x="%s", y="%s"',model,xstr,ystr)
        
        model = get_model(model) 
        self.model_fn = model
        npar = len(parstr.split(','))
        
        # get data values
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
            
        # get p0
        self.p0_str = self.model_p0.get()
        p0 = self.p0_str
        if p0[-1] == ',': p0 = p0[:-1]
        
        try:
            if p0:  p0 = list(map(float,p0.split(',')))
            else:   p0 = np.ones(npar)
        except ValueError:
            msg = 'Bad p0 input: use format p0,p1,p2,...'
            messagebox.showerror('Error',msg)
            self.logging.error('Bad p0 input')
            raise ValueError(msg) from None
        
        if len(p0) < npar:  p0 = np.concatenate((p0,np.ones(npar-len(p0))))
        if len(p0) > npar:  p0 = p0[:npar]
            
        # fit model 
        if all(np.isnan(yerrs)): yerrs = None
        
        par,cov = curve_fit(model,xvals,yvals,sigma=yerrs,absolute_sigma=True,p0=p0)
        std = np.diag(cov)**0.5
        
        if yerrs is None:   yerrs = np.ones(len(xvals))
        chi = np.sum(((model(xvals,*par)-yvals)/yerrs)**2)/(len(xvals)-npar)
        
        # display results 
        number = '%'+('%.df' % self.bfit.rounding)
        outtext = [p+': '+number % r for p,r in zip(parlst,par)]
        self.model_results_text.delete('1.0',END)
        self.result_str = '\n'.join(outtext)
        self.model_results_text.insert('1.0',self.result_str)
        
        outtext = [number % r for r in std]
        self.model_errors_text.delete('1.0',END)
        self.error_str = '\n'.join(outtext)
        self.model_errors_text.insert('1.0',self.error_str)
        
        self.model_chi_label['text'] = 'ChiSq: %.2f' % np.around(chi,2)
        
        self.logger.info('Fit model results: %s, Errors: %s',str(par),str(std))
        
        self.model_results = (par,std)
        self.fittab.draw_param()
        self.draw_model()    
        
    # ======================================================================= #
    def draw_model(self,*args):
        figstyle = 'param'
        
        # get draw components
        xstr = self.fittab.xaxis.get()
        ystr = self.fittab.yaxis.get()
        
        self.logger.info('Draw model parameters "%s" vs "%s"',ystr,xstr)
        
        # get data values
        try:
            xvals, xerrs = self.fittab.get_values(xstr)
            yvals, yerrs = self.fittab.get_values(ystr)
        except UnboundLocalError as err:
            self.logger.error('Bad input parameter selection')
            messagebox.showerror("Error",'Select two input parameters')
            raise err from None
        except (KeyError,AttributeError) as err:
            self.logger.error('Parameter "%s or "%s" not found for drawing model',
                              xstr,ystr)
            messagebox.showerror("Error",
                    'Parameter "%s" or "%s" not found' % (xstr,ystr))
            raise err from None

        # get fit function
        fn = self.model_fn

        # get draw style
        style = self.bfit.draw_style.get()
        
        if style == 'new':
            self.fittab.plt.figure(figstyle)
        elif style == 'redraw':
            self.fittab.plt.clf(figstyle)
        
        self.fittab.plt.gca(figstyle)
            
        # draw
        fitx = np.linspace(min(xvals),max(xvals),self.fittab.n_fitx_pts)
        f = self.fittab.plt.plot(figstyle,fitx,fn(fitx,*self.model_results[0]),color='k')
        
        # plot elements
        self.fittab.plt.xlabel(figstyle,xstr)
        self.fittab.plt.ylabel(figstyle,ystr)
        self.fittab.plt.tight_layout(figstyle)
        
        raise_window()
    
