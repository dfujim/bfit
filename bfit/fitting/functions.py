# Base functions used in fitting bnmr data
# Derek Fujimoto
# June 2018
from bfit.fitting.integrator import PulsedFns
import numpy as np

# =========================================================================== #
class fake_code(dict):
    """For faking code objects"""
    def __getattr__(self,name):
        return self[name]

# =========================================================================== #
# TYPE 1 FUNCTIONS
# =========================================================================== #
def lorentzian(freq,peak,width,amp):
    return -amp*0.25*np.square(width)/(np.square(freq-peak)+np.square(0.5*width))

def gaussian(freq,peak,width,amp):
    return -amp*np.exp(-np.square((freq-peak)/(width))/2)

# =========================================================================== #
# TYPE 2 PULSED FUNCTIONS 
# =========================================================================== #
class pulsed(object):
    """Pulsed function base class"""
    
    def __init__(self,lifetime,pulse_len):
        """
            lifetime: probe lifetime in s
            pulse_len: length of pulse in s
        """
        self.pulser = PulsedFns(lifetime,pulse_len)
    
class pulsed_exp(pulsed):
    __code__= fake_code([('co_varnames',['time','lambda_s','amp'])])
    def __call__(self,time,lambda_s,amp):
        return amp*self.pulser.exp(time,lambda_s)
        
class pulsed_strexp(pulsed):
    __code__= fake_code([('co_varnames',['time','lambda_s','beta','amp'])])
    def __call__(self,time,lambda_s,beta,amp):
        return amp*self.pulser.strexp(time,lambda_s,beta)

# =========================================================================== #
# FUNCTION SUPERPOSITION
# =========================================================================== #
def get_fn_superpos(fn_handles):
    """
        Return a function which takes the superposition of a number of the same 
        function.
        
        fn_handles: list of function handles that should be superimposed
        
        return fn_handle
    """
    
    npars = [0]+[len(f.__code__.co_varnames)-1 for f in fn_handles]
    
    # make function
    def fn(x,*pars):
        val = lambda fn,ilo,ihi: fn(x,*pars[ilo:ihi])
        return np.sum((val(f,l,h) for f,l,h in zip(fn_handles,npars[:-1],
                                                   npars[1:])))
    return fn
