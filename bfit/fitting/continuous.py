# Fit frequency scan data with multipeaked curves
# Derek Fujimoto
# June 2018

from bdata import bdata
from scipy.optimize import curve_fit
import numpy as np

# number of input parameters (not detectable)
ninputs_dict = {'lor':3,'gaus':3,'2lor_shpk':5}

# ========================================================================== #
def fscan(data,mode,omit='',ncomp=1,probe='8Li',hist_select='',**kwargs):
    """
        Fit combined asymetry from 1F run: frequency scan. 
    
        data: tuple of (xdata,ydata,yerr,life) OR bdata object.
            xdata:  np array of xaxis data to fit.
            ydata:  np array of yaxis data to fit.
            yerr:   np array of error in ydata.
            life:   probe lifetime in s.
        mode:           one of "lor, gauss, 2lor_shpk".
        omit:           string of space-separated bin ranges to omit
        ncomp:          number of compenents. Ex: for exp+exp set ncomp=2. 
        probe:          string for probe species. Tested only for 8Li. 
        hist_select:    string for selecting histograms to use in asym calc
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: par,cov,fn
            par: best fit parameters
            cov: covariance matrix
            fn:  function pointer to fitted function
            
        Note: always fits baseline
    """

    # Check data input
    if type(data) == bdata:
        xdata,ydata,yerr = data.asym('c',omit=omit,hist_select=hist_select)
        life = data.life[probe][0]
    else:
        xdata,ydata,yerr,life = data
    
    # check for values with error == 0. Omit these values. 
    tag = yerr != 0
    xdata = xdata[tag]
    ydata = ydata[tag]
    yerr = yerr[tag]
    
    # check ncomponents
    if ncomp < 1:
        raise RuntimeError('ncomp needs to be >= 1')
        
    # Get fitting function 
    if mode == 'lor':
        fn1 = lor
    elif mode == 'gaus':
        fn1 = gaus
    elif mode == '2lor_shpk':
        fn1 = lor2_shrpk
    
    # Make final function based on number of components
    ninputs = ninputs_dict[mode]
    npars = ninputs*ncomp+1    
    
    def fitfn(x,*pars):
        val = lambda i : fn1(x,*tuple(pars[i*ninputs:(i+1)*ninputs]))
        return np.sum(i for i in map(val,range(ncomp)))+pars[-1]
    
    # Make initial parameters
    if 'p0' in kwargs.keys():
        if len(kwargs['p0']) < npars: 
            raise ValueError('Inconsistent shapes between p0 and `x0`.')
    else:
        kwargs['p0'] = np.zeros(npars)+1
        
    # Fit the function 
    par,cov = curve_fit(fitfn,xdata,ydata,sigma=yerr,**kwargs)
    
    # get chisquared
    chi = np.sum(np.square((ydata-fitfn(xdata,*tuple(par)))/yerr))/(len(ydata)-1)
    
    return (par,cov,chi,fitfn)
    
# ========================================================================== #
# FITTING FUNCTIONS
def lor(freq,peak,width,amp):
    """Lorentzian"""
    return -amp*0.25*np.square(width)/(np.square(freq-peak)+np.square(0.5*width))

def lor2_shrpk(freq,peak,width1,amp1,width2,amp2):
    """Two Lorentzians with shared peak value"""
    return -amp1*0.25*np.square(width1)/(np.square(freq-peak)+np.square(0.5*width1))+\
            -amp2*0.25*np.square(width2)/(np.square(freq-peak)+np.square(0.5*width2))

def gaus(freq,peak,width,amp):
    return -amp*np.exp(-np.square((freq-peak)/(width))/2)



