# Fit data with pulsed curves
# Derek Fujimoto
# June 2018

from bfit.fitting.integrator import PulsedFns
from bdata import bdata
from scipy.optimize import curve_fit
import numpy as np
import bfit.fitting.functions as fns

# number of input parameters (not detectable)
ninputs_dict = {'exp':2,'strexp':3,'mixed_strexp':6}

# ========================================================================== #
def slr(data,mode,rebin=1,offset=False,ncomp=1,probe='8Li',hist_select='',**kwargs):
    """
        Fit combined asymetry from pulsed beam SLR data: time scan. 
    
        data: tuple of (xdata,ydata,yerr,life,pulse) OR bdata object.
            xdata:  np array of xaxis data to fit.
            ydata:  np array of yaxis data to fit.
            yerr:   np array of error in ydata.
            life:   probe lifetime in s.
            pulse:  duration of beam-on time in s.
        mode:           one of "strexp, mixed_strexp, exp".
        rebin:          rebinning of data prior to fitting. 
        offset:         if True, include offset parameter in fitting function.
                            ensure that p0[-1] = offset, if specified. 
        ncomp:          number of compenents. Ex: for exp+exp set ncomp=2. 
        probe:          string for probe species. Tested only for 8Li. 
        hist_select:    string for selecting histograms to use in asym calc
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: par,cov,chi,fn
            par: best fit parameters
            cov: covariance matrix
            chi: chisquared
            fn:  function pointer to fitted function
    """

    # Check data input
    if type(data) == bdata:
        xdata,ydata,yerr = data.asym('c',rebin=rebin,hist_select=hist_select)
        life = data.life[probe][0]
        pulse = data.ppg.dwelltime.mean*data.ppg.beam_on.mean/1000.
    else:
        xdata,ydata,yerr,life,pulse = data
    
    # check for values with error == 0. Omit these values. 
    tag = yerr != 0
    xdata = xdata[tag]
    ydata = ydata[tag]
    yerr = yerr[tag]
    
    # check ncomponents
    if ncomp < 1:
        raise RuntimeError('ncomp needs to be >= 1')
    
    # Get fitting function 
    if mode == 'strexp':
        fn1 = fns.pulsed_strexp(life,pulse)
    elif mode == 'exp':
        fn1 = fns.pulsed_exp(life,pulse)

    # Make final function based on number of components
    fnlist = [fn1]*ncomp
    
    if offset:
        fnlist.append(lambda x,b: b)
    
    fitfn = fns.get_fn_superpos(fnlist)
    npars = len(fnlist)
            
    # Make initial parameters
    if 'p0' in kwargs.keys():
        if len(kwargs['p0']) < npars: 
            raise ValueError('Inconsistent shapes between p0 and `x0`.')
    else:
        kwargs['p0'] = np.zeros(npars)+1
    
    # Fit the function 
    par,cov = curve_fit(fitfn,xdata,ydata,sigma=yerr,**kwargs)
    
    # get chisquared
    chi = np.sum(np.square((ydata-fitfn(xdata,*par))/yerr))/(len(ydata)-1)
    
    return (par,cov,chi,fitfn)
