# Fit list of bdata objects with function list
# Derek Fujimoto
# Nov 2018

from bdata import bdata
from scipy.optimize import curve_fit
import numpy as np
from bfit.fitting.global_bdata_fitter import global_bdata_fitter
import collections

# ========================================================================== #
def fit_list(runs,years,fnlist,omit=None,rebin=None,sharelist=None,npar=-1,
              hist_select='',**kwargs):
    """
        Fit combined asymetry from bdata.
    
        runs:           list of run numbers
        
        years:          list of years corresponding to run numbers, or int which applies to all
        
        fnlist:         list of function handles to fit (or single which applies to all)
                        must specify inputs explicitly (do not do def fn(*par)!)
                        must have len(fn) = len(runs) if list
        
        omit:           list of strings of space-separated bin ranges to omit
        rebin:          list of rebinning of data prior to fitting. 
        
        sharelist:      list of bool to indicate which parameters are shared. 
                        True if shared
                        len = number of parameters.
        
        npar:           number of free parameters in each fitting function.
                        Set if number of parameters is not intuitable from 
                            function code.      
        
        hist_select:    string for selecting histograms to use in asym calc
        
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: par,cov
            par: best fit parameters
            std: standard deviation for each parameter
    """
    
    nruns = len(runs)
    
    # get fnlist
    if not isinstance(fnlist,collections.Iterable):
        fnlist = [fnlist]
    
    # get number of parameters
    if npar < 0:
        npar = fnlist[0].__code__.co_argcount-1

    # get fnlist again
    fnlist.extend([fnlist[-1] for i in range(nruns-len(fnlist))])

    # get sharelist
    if type(sharelist) == type(None):
        sharelist = np.zeros(npar,dtype=bool)

    # get omit
    if type(omit) == type(None):
        omit = ['']*nruns
    elif len(omit) < nruns:
        omit = np.concatenate(omit,['']*(nruns-len(omit)))
        
    # get rebin
    if type(rebin) == type(None):
        rebin = np.ones(nruns)
    elif len(rebin) < nruns:
        rebin = np.concatenate(rebin,[1]*(nruns-len(rebin)))

    # get years
    if type(years) in (int,float):
        years = np.ones(nruns,dtype=int)*years
        
    # get p0 list
    if 'p0' in kwargs.keys():
        p0 = kwargs['p0']
        del kwargs['p0']
    else:
        p0 = [np.ones(npar)]*nruns

    # get bounds
    if 'bounds' in kwargs.keys():
        bounds = kwargs['bounds']
        del kwargs['bounds']
    else:
        bounds = [(np.inf,np.inf)]*nruns

    # fit globally -----------------------------------------------------------
    if any(sharelist):
        g = global_bdata_fitter(runs,years,fnlist,sharelist,npar)
        g.fit(**kwargs)
        _,chis = g.get_chi()
        pars,stds = g.get_par()
        
    # fit runs individually --------------------------------------------------
    else:
        pars = []
        stds = []
        chis = []
        for r,y,fn,om,re,p,b in zip(runs,years,fnlist,omit,rebin,p0,bounds):
            p,s,c = fit_single(r,y,fn,om,re,hist_select,p0=p,bounds=b,**kwargs)
            pars.append(p)
            stds.append(s)
            chis.append(c)
            
    return(pars,stds,chis)

# =========================================================================== #
def fit_single(run,year,fn,omit='',rebin=1,hist_select='',**kwargs):
    """
        Fit combined asymetry from bdata.
    
        runs:           run number
        
        years:          year
        
        fn:             function handle to fit
        
        omit:           string of space-separated bin ranges to omit
        rebin:          rebinning of data prior to fitting. 
        
        hist_select:    string for selecting histograms to use in asym calc
        
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: par,cov
            par: best fit parameters
            std: standard deviation for each parameter
    """
    
    # Get data input
    data = bdata(run,year)
    x,y,dy = data.asym('c',omit=omit,rebin=rebin,hist_select=hist_select)
    
    # check for values with error == 0. Omit these values. 
    tag = dy != 0
    x = x[tag]
    y = y[tag]
    dy = dy[tag]
    
    # p0
    if 'p0' not in kwargs.keys():
        kwargs['p0'] = np.ones(fn.__code__.co_argcount-1)
    
    # Fit the function 
    par,cov = curve_fit(fn,x,y,sigma=dy,**kwargs)
    std = np.sqrt(np.diag(cov))
    dof = len(y)-fn.__code__.co_argcount+1
    
    # get chisquared
    chi = np.sum(np.square((y-fn(x,*par))/dy))/dof
    
    return (par,std,chi)
