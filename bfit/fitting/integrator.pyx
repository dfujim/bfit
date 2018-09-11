# Cython functions for fast numerical integration 
# Derek Fujimoto
# October 2017
#
# Based on the work of John D. Cook
# https://www.johndcook.com/blog/double_exponential_integration/
# Note: to see slow lines write 'cython integrator.pyx -a --cplus'

# To build write: python setup_integrator.py build_ext --inplace
# assuming the cython seup file is called setup_integrator.

# python3 setup_integrator.py build_ext --inplace

cimport cython
import numpy as np
cimport numpy as np
from libc.math cimport exp 

# ========================================================================== #
# Integration functions import
cdef extern from 'integration_fns.h':
    cdef cppclass Integrator:
        double lifetime;
        Integrator(double);
        double StrExp(double,double,double,double) except +;
        double MixedStrExp(double,double,double,double,double,double,double) except +;
        
# =========================================================================== #
# Integrator class
cdef class PulsedFns:
    cdef double life            # probe lifetime in s
    cdef double pulse_len       # length of beam on in s

# =========================================================================== #
    def __init__(self,lifetime,pulse_len):
        """
            Inputs:
                lifetime: probe lifetime in s
                pulse_len: beam on pulse length in s
        """
        self.life = lifetime
        self.pulse_len = pulse_len

# =========================================================================== #
    @cython.boundscheck(False)  # some speed up in exchange for instability
    cpdef exp(self,np.ndarray[double, ndim=1] time,double Lambda,
                   double amp):
        """
            Pulsed exponential for an array of times. Efficient c-speed looping 
            and indexing. 
            
            Inputs: 
                time: array of times
                Lambda: 1/T1 in s^-1
                Amp: amplitude
                
            Outputs: 
                np.array of values for the puslsed stretched exponential. 
        """
        
        # Variable definitions
        cdef int n = time.shape[0]
        cdef int i
        cdef double t
        cdef np.ndarray[double, ndim=1] out = np.zeros(n)
        cdef double life = self.life
        cdef double pulse_len = self.pulse_len
        cdef double prefac
        cdef double lambda1
        cdef double afterfactor
        
        # precalculations 
        lambda1 = Lambda+1./life
        prefac = amp/(lambda1*life)
        afterfactor = (1-np.exp(-lambda1*pulse_len))/(1-np.exp(-pulse_len/life))
        
        # Calculate pulsed exponential
        for i in range(n):    
            
            # get some useful values: time, normalization
            t = time[i]
        
            # during pulse
            if t<pulse_len:
                out[i] = prefac*(1-np.exp(-lambda1*t))/(1-np.exp(-t/life))
            
            # after pulse
            else:
                out[i] = prefac*afterfactor*np.exp(-Lambda*(t-pulse_len))
        
        return out

# =========================================================================== #
    @cython.boundscheck(False)  # some speed up in exchange for instability
    cpdef str_exp(self,np.ndarray[double, ndim=1] time,double Lambda, 
                         double Beta, double amp):
        """
            Pulsed stretched exponential for an array of times. Efficient 
            c-speed looping and indexing. 
            
            Inputs: 
                time: array of times
                Lambda: 1/T1 in s^-1
                Beta: stretching factor
                Amp: amplitude
                
            Outputs: 
                np.array of values for the puslsed stretched exponential. 
        """
        
        # Variable definitions
        cdef double out
        cdef int n = time.shape[0]
        cdef int i
        cdef double t, x
        cdef np.ndarray[double, ndim=1] out_arr = np.zeros(n)
        cdef double prefac
        cdef double life = self.life
        cdef double pulse_len = self.pulse_len
        
        # Calculate pulsed str. exponential
        for i in range(n):    
            
            # get some useful values: time, normalization
            t = time[i]
            prefac = life*(1.-exp(-t/life))
        
            # prefactor special case
            if prefac == 0:
                out_arr[i] = np.inf
                continue
            
            # make integrator
            intr = new Integrator(life)
            
            # during pulse
            if t<pulse_len:
                x = intr.StrExp(t,t,Lambda,Beta)
                out = amp*x/prefac
            
            # after pulse
            else:
                x = intr.StrExp(t,pulse_len,Lambda,Beta)
                out = amp/prefac*x*exp((t-pulse_len)/life)
            
            # save result
            out_arr[i] = out
        
        return out_arr

# =========================================================================== #
    @cython.boundscheck(False)  # some speed up in exchange for instability
    cpdef mixed_str_exp(self,np.ndarray[double, ndim=1] time, 
                double Lambda1, double Beta1, double Lambda2, double Beta2,
                double alpha, double amp):
        """
            Pulsed stretched exponential for an array of times. Efficient 
            c-speed looping and indexing. 
            
            Inputs: 
                time: array of times
                pulse_len: pulse length
                Lambda: 1/T1 in s^-1
                Beta: stretching factor
                alpha: mixing 0 < alpha < 1
                
            Outputs: 
                np.array of values for the puslsed stretched exponential. 
        """
        
        # Variable definitions
        cdef double out
        cdef int n = time.shape[0]
        cdef int i
        cdef double t
        cdef np.ndarray[double, ndim=1] out_arr = np.zeros(n)
        cdef double prefac
        cdef double life = self.life
        cdef double pulse_len = self.pulse_len
        
        # Calculate pulsed str. exponential
        for i in range(n):    
            
            # get some useful values: time, normalization
            t = time[i]
            prefac = life*(1.-exp(-t/life))
        
            # prefactor special case
            if prefac == 0:
                out_arr[i] = np.inf
                continue
            
            # make integrator
            intr = new Integrator(life)
            
            # during pulse
            if t<pulse_len:
                x = intr.MixedStrExp(t,t,Lambda1,Beta1,Lambda2,Beta2,alpha)
                out = amp*x/prefac
            
            # after pulse
            else:
                x = intr.MixedStrExp(t,pulse_len,Lambda1,Beta1,Lambda2,Beta2,
                                     alpha)
                out = amp/prefac*x*exp((t-pulse_len)/life)
            
            # save result
            out_arr[i] = out
        
        return out_arr
