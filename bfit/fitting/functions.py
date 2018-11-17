# Base functions used in fitting bnmr data
# Derek Fujimoto
# June 2018
from bfit.fitting.integrator import PulsedFns
import numpy as np

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
    def __call__(self,time,lambda_s,amp):
        return amp*self.pulser.exp(time,lambda_s)
        
class pulsed_str_exp(pulsed):
    def __call__(self,time,lambda_s,beta,amp):
        return amp*self.pulser.strexp(time,lambda_s,beta)

        
# =========================================================================== #
# FUNCTION SUPERPOSITION
# =========================================================================== #
def get_fn_superpos(fn_handle,ncomp):
    
    def fn(x,*pars):
        
        out = 
