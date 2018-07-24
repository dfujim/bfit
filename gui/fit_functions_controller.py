# Object for interfacing the fit functions and fitting tools to bfit
# Derek Fujimoto
# Feb 2018

import numpy as np
from integrator import Integrator
from bdata import bdata
from types import NoneType

__doc__="""
    Interface the fitting backend to the frontend. Provides a template for 
    custom fitting backends.
    
    Derek Fujimoto
    February 2018
"""

# =========================================================================== #
# =========================================================================== #
class fit_functions_controller(object):
    """
        Data Fields
            fn:             fitting function pointer
            results:        fitting results dictionary. Keys in fit docstring.
            data:           list of bdata object
            mode:           data mode (20,1f,1n)
            shared:         list of booleans for setting global variables 
            p0:             list of initial parameters
            bounds:         list of parameter bounds
            option_string:  string for additional options
            functions_names:dictionary of all function names for each run mode
            function_link:  dictionary of function pointers for each function 
    """
    
    # functions available for each run mode
    functions_names = {'20':('Exp','StrExp','Exp+C','StrExp+C'),
                   '1f':('Lorentzian','Gaussian','Lorentzian+C','Gaussian+C'),
                   '1n':('Lorentzian','Gaussian','Lorentzian+C','Gaussian+C')}
    
    # link function names to defined function in object
    function_link = {'Exp':self.exp,'StrExp':self.strep,'Exp+C':self.exp_c,
                     'StrExp+C':self.strexp_c,'Lorentzian':self.lorentzian,
                     'Gaussian':self.gaussian}
    
    # ======================================================================= #
    def __init__(self,bdata_list,mode,shared_param,init_param,bounds,
                 ncomponents,probe,option_string):
        """
        """
        
        # set instance variables
        self.fn = None
        self.results = None
        self.data = bdata_list
        self.mode = mode
        self.shared = shared_param
        self.p0 = init_param
        self.bounds = bounds
        self.ncomponents = ncomponents
        self.option_string = option_string
        self.life = bdata_list.life[probe][0]
        
    # ======================================================================= #
    def select_fn(self,selection):
        """Set the function to fit"""
        
        try:
            self.fn = function_link[selection]
        except KeyError:
            raise KeyError('Function not implemented')
        
    # ======================================================================= #
    def fit(self):
        """Call imported fitting function. Set fit results. Dictionary should 
        have the following keys:
        
        General fit output keys: 
                chisq
                
            Function specific output keys:
                Exp:        A0,Lambda
                Exp+C:      A0,Lambda,C
                StrExp:     A0,Lambda,Beta
                StrExp+C:   A0,Lambda,Beta,C
                Lorentzian: Amp,Peak,Width
                Gaussian:   Amp,Peak,Width
        """
        
    # ======================================================================= #
    def get_fit_results(self):
        """Return fit results dictionary.  
            
            General fit output keys: 
                chisq
                
            Function specific output keys:
                Exp:        A0,Lambda
                Exp+C:      A0,Lambda,C
                StrExp:     A0,Lambda,Beta
                StrExp+C:   A0,Lambda,Beta,C
                Lorentzian: Amp,Peak,Width
                Gaussian:   Amp,Peak,Width
        """
        
        
        if type(self.results) != NoneType:
            return self.results
        else:
            return None
            
    # ======================================================================= #
    def exp(self,x,A0,Lambda):
        """
            Equation: A0*exp(-x*Lambda), pulsed
        """
        pass

    # ======================================================================= #
    def exp_c(self,x,A0,Lambda,C):
        """
            Equation: A0*exp(-x*Lambda)+C, pulsed
        """
        pass

    # ======================================================================= #
    def strexp(self,x,A0,Lambda,Beta):
        """
            Equation: A0*exp(-(x*Lambda)**Beta), pulsed
        """
        pass

    # ======================================================================= #
    def strexp_c(self,x,A0,Lambda,Beta,C):
        """
            Equation: A0*exp(-(x*Lambda)**Beta)+C, pulsed
        """
        pass

    # ======================================================================= #
    def lorentzian(self,x,peak,width,amp,C):
        """
            Equation: -amp*0.25*width**2/((x-peak)**2+(0.5*width)**2)+C
        """
        return -amp*0.25*width**2/((x-peak)**2+(0.5*width)**2)+C

    # ======================================================================= #
    def gaussian(self,x,peak,width,amp,C):
        """
            Equation: amp*exp(-((x-peak)/width)**2)+C
        """
        return amp*exp(-((x-peak)/width)**2)+C

