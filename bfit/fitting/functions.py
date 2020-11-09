# Base functions used in fitting bnmr data
# Derek Fujimoto
# June 2018
from bfit.fitting.integrator import PulsedFns
import numpy as np

# =========================================================================== #
class code_wrapper(object):
    """Wrap code object such that attemps to access co_varnames excludes self"""
    def __init__(self,obj):
        self.co_varnames = obj.co_varnames[1:]
        self.co_argcount = obj.co_argcount-1
        self.obj = obj
    
    def __getattr__(self,name):
        try:
            return self.__dict__[name]
        except KeyError:
            return getattr(self.obj,name)

# =========================================================================== #
# TYPE 1 FUNCTIONS
# =========================================================================== #
def lorentzian(freq, peak, fwhm, amp):
    return -amp*np.square(fwhm)/(np.square(freq-peak)+np.square(fwhm))

def bilorentzian(freq, peak, fwhmA, ampA, fwhmB, ampB):
    return -ampA*0.25*np.square(fwhmA)/(np.square(freq-peak)+np.square(0.5*fwhmA))\
           -ampB*0.25*np.square(fwhmB)/(np.square(freq-peak)+np.square(0.5*fwhmB))

def gaussian(freq, mean, sigma, amp):
    return -amp*np.exp(-np.square((freq-mean)/(sigma))/2)

def quadlorentzian(freq, nu_0, nu_q, eta, theta, phi, 
                   amp0, amp1, amp2, amp3, 
                   fwhm0, fwhm1, fwhm2, fwhm3, I):
    """
        nu_q = quadrupole frequency = 3e^2Qq/4I(2I-1)
        eta =  EFG asymmetry [0, 1]
        theta = polar angle (beta in notation of Euler angles in the paper)
        phi = polar angle (alpha in notation of Euler angles in the paper)
        m = magnetic sublevel for the m -> m - 1 transition
    
        amp: amplitudes of each of the peaks
        fwhm: FWHM of each of the peaks
    """
    
    # get the peak locations
    peaks = [qp_nu(nu_0, nu_q, eta, theta, phi, I, m) for m in np.arange(-(I-1),I+1,1)]
    
    # get each lorentzian
    lor0 = lorentzian(freq, peaks[0], fwhm0, amp0)
    lor1 = lorentzian(freq, peaks[1], fwhm1, amp1)
    lor2 = lorentzian(freq, peaks[2], fwhm2, amp2)
    lor3 = lorentzian(freq, peaks[3], fwhm3, amp3)   
    
    return lor0+lor1+lor2+lor3
    
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
    
    def __call__(self):pass
    
    def __getattr__(self,name):
        if name == '__code__':
            return code_wrapper(self.__call__.__code__)
        else:
            try:
                return self.__dict__[name]
            except KeyError as err:
                raise AttributeError(err) from None
            
class pulsed_exp(pulsed):
    def __call__(self,time,lambda_s,amp):
        return amp*self.pulser.exp(time,lambda_s)

class pulsed_biexp(pulsed):
    def __call__(self, time, lambda_s, lambdab_s, fracb, amp):
        return amp*((1-fracb)*  self.pulser.exp(time, lambda_s) + \
                    fracb*      self.pulser.exp(time, lambdab_s))
        
class pulsed_strexp(pulsed):
    def __call__(self, time, lambda_s, beta, amp):
        return amp*self.pulser.str_exp(time, lambda_s, beta)

# =========================================================================== #
# HELPER FUNCTIONS
# =========================================================================== #

# ----------------------------------------------------------------------------
# function superposition
def get_fn_superpos(fn_handles):
    """
        Return a function which takes the superposition of a number of the same 
        function.
        
        fn_handles: list of function handles that should be superimposed
        
        return fn_handle
    """
    
    npars = np.cumsum([0]+[len(f.__code__.co_varnames)-1 for f in fn_handles])

    # make function
    def fn(x,*pars):
        return np.sum(f(x,*pars[l:h]) for f,l,h in zip(fn_handles,npars[:-1],npars[1:]))
    return fn

# ----------------------------------------------------------------------------
# quadrupole perturbations to NMR frequency
def qp_1st_order(nu_q, eta, theta, phi, m):
    """
        1st order quadrupole purturbation to NMR frquencies
        
        returns frequencies for m = -1 to 2 transition
        nu_q = 3e^2Qq/4I(2I-1)
        see e.g.,:
        P. P. Man, "Qaudrupolar Interactions", in Encyclopedia of Magnetic
        Resonance, edited by R. K. Harris and R. E. Wasylishen.
        https://doi.org/10.1002/9780470034590.emrstm0429.pub2
        
        Written by Ryan McFadden, translated to python by Derek Fujimoto

        nu_q = quadrupole frequency = 3e^2Qq/4I(2I-1)
        eta =  EFG asymmetry [0, 1]
        theta = polar angle (beta in notation of Euler angles in the paper)
        phi = polar angle (alpha in notation of Euler angles in the paper)
        m = magnetic sublevel for the m -> m - 1 transition
    """  


    # Equation (28)
    V_0 = np.sqrt(1.5) * 0.5 * (3 * np.square(np.cos(theta)) - 1 + \
                eta * np.square(np.sin(theta)) * np.cos(2 * phi))

    # Equation (23)
    return nu_q * (np.sqrt(6) / 3) * (1 - 2 * m) * V_0

def qp_2nd_order(nu_0, nu_q, eta, theta, phi, I, m):
    """
        2nd order quadrupole purturbation to NMR frquencies
        
        returns frequencies for m = -1 to 2 transition
        nu_q = 3e^2Qq/4I(2I-1)
        see e.g.,:
        P. P. Man, "Qaudrupolar Interactions", in Encyclopedia of Magnetic
        Resonance, edited by R. K. Harris and R. E. Wasylishen.
        https://doi.org/10.1002/9780470034590.emrstm0429.pub2
        
        Written by Ryan McFadden, translated to python by Derek Fujimoto
    
        nu_0 = Larmor frequency
        nu_q = quadrupole frequency = 3e^2Qq/4I(2I-1)
        eta =  EFG asymmetry [0, 1]
        theta = polar angle (beta in notation of Euler angles in the paper)
        phi = polar angle (alpha in notation of Euler angles in the paper)
        I = spin quantum number
        m = magnetic sublevel for the m -> m - 1 transition
    """
  
    # Equation (32a)
    V_m1V_1 = -1.5 * ((-1/3 * np.square(eta * np.cos(2*phi)) + 2 * eta * \
              np.cos(2*phi)) * np.cos(theta)**4 + \
              (2/3 * np.square(eta * np.cos(2*phi)) - 2 * eta * np.cos(2*phi) - \
              (eta * eta / 3) + 3) * np.square(np.cos(theta)) + \
              (eta * eta / 3) * (1 - np.square(np.cos(2*phi))))

    # Equation (32b)
    V_m2V_2 = 1.5 * (((1.0 / 24.0) * np.square(eta * np.cos(2*phi)) - \
                     0.25 * eta * np.cos(2*phi) + 3/8) * \
                     np.cos(theta)**4 + ((-1.0 / 12.0) * np.cos(2*phi) * np.cos(2*phi) + \
                     (eta * eta / 6.0) - 0.75) * np.square(np.cos(theta)) + \
                    (1.0 / 24.0) * np.square(eta * np.cos(2*phi)) + \
                    0.25 * eta * np.cos(2*phi) + 3/8)

    # Equation (25)
    return (-2/nu_0) * np.square(nu_q / 3.0) * \
         (1.0 * V_m1V_1 * (24.0 * m * (m - 1.0) - 4.0 * I * (I + 1.0) + 9.0) + \
          0.5 * V_m2V_2 * (12.0 * m * (m - 1.0) - 4.0 * I * (I + 1.0) + 6.0))

def qp_nu(nu_0, nu_q, eta, theta, phi, I, m): 
    """
        Helper function for returning the 0th-, 1st-, and 2nd-order frequencies 
        to quadrupole perturbed Zeeman Hamiltonian

        Written by Ryan McFadden, translated to python by Derek Fujimoto
        
        nu_0 = Larmor frequency
        nu_q = quadrupole frequency = 3e^2Qq/4I(2I-1)
        eta =  EFG asymmetry [0, 1]
        theta = polar angle (beta in notation of Euler angles in the paper)
        phi = polar angle (alpha in notation of Euler angles in the paper)
        I = spin quantum number
        m = magnetic sublevel for the m -> m - 1 transition
    """
    # Equation (26)
    return nu_0 + qp_1st_order(nu_q, eta, theta, phi, m) + \
           qp_2nd_order(nu_0, nu_q, eta, theta, phi, I, m)
