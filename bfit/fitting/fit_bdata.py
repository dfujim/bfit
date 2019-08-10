# Fit list of bdata objects with function list
# Derek Fujimoto
# Nov 2018

import collections
import numpy as np
from bdata import bdata
from scipy.optimize import curve_fit
from tqdm import tqdm
from bfit.fitting.global_bdata_fitter import global_bdata_fitter

# ========================================================================== #
def fit_list(runs,years,fnlist,omit=None,rebin=None,sharelist=None,npar=-1,
              hist_select='',xlims=None,asym_mode='c',fixed=None,**kwargs):
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
        
        xlims:          list of 2-tuple for (low,high) bounds on fitting range 
                            based on x values
        
        asym_mode:      input for asymmetry calculation type 
                            c: combined helicity
                            h: split helicity
                            
                        For 2e mode, prefix with:
                            sl_: combined timebins using slopes
                            dif_: combined timebins using differences
                            raw_: raw time-resolved 
                            
                            ex: sl_c or raw_h or dif_c
        
        fixed:          list of booleans indicating if the paramter is to be 
                        fixed to p0 value (same length as p0). Returns best 
                        parameters in order presented, with the fixed 
                        parameters omitted. Can be a list of lists with one list 
                        for each run.
        
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: (par,cov,ch,gchi)
            par: best fit parameters
            cov: covariance matrix
            chi: chisquared of fits
            gchi:global chisquared of fits
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
    if sharelist is None:
        sharelist = np.zeros(npar,dtype=bool)

    # get omit
    if omit is None:
        omit = ['']*nruns
    elif len(omit) < nruns:
        omit = np.concatenate(omit,['']*(nruns-len(omit)))
        
    # get rebin
    if rebin is None:
        rebin = np.ones(nruns)
    elif type(rebin) is int:
        rebin = np.ones(nruns)*rebin
    elif len(rebin) < nruns:
        rebin = np.concatenate((rebin,np.ones(nruns-len(rebin))))
    
    rebin = np.asarray(rebin).astype(int)
    
    # get years
    if type(years) in (int,float):
        years = np.ones(nruns,dtype=int)*years
        
    # get p0 list
    if 'p0' in kwargs.keys():
        p0 = kwargs['p0']
        del kwargs['p0']
    else:
        p0 = [np.ones(npar)]*nruns

    # fit globally -----------------------------------------------------------
    if any(sharelist) and len(runs)>1:
        print('Running shared parameter fitting...')
        g = global_bdata_fitter(runs,years,fnlist,sharelist,npar,xlims,
                                asym_mode=asym_mode,rebin=rebin,fixed=fixed)
        g.fit(p0=p0,**kwargs)
        gchi,chis = g.get_chi() # returns global chi, individual chi
        pars,covs = g.get_par()
        
    # fit runs individually --------------------------------------------------
    else:
        
        # get bounds
        if 'bounds' in kwargs.keys():
            bounds = kwargs['bounds']
            del kwargs['bounds']
        else:
            bounds = [(-np.inf,np.inf)]*nruns 
            
        # check p0 dimensionality
        if len(np.asarray(p0).shape) < 2:
            p0 = [p0]*nruns
        
        # check xlims shape - should match number of runs
        if xlims is None:
            xlims = [None]*nruns
        elif len(np.asarray(xlims).shape) < 2:
            xlims = [xlims for i in range(nruns)]
        else:
            xlims = list(xlims)
            xlims.extend([xlims[-1] for i in range(len(runs)-len(xlims))])
        
        # check fixed shape
        if fixed is not None: 
            fixed = np.asarray(fixed)
            if len(fixed.shape) < 2:
                fixed = [fixed]*nruns
        else:
            fixed = [[False]*npar]*nruns
        
        pars = []
        covs = []
        chis = []
        gchi = 0.
        dof = 0.
        
        iter_obj = tqdm(zip(runs,years,fnlist,omit,rebin,p0,bounds,xlims,fixed),
                        total=len(runs),desc='Independent Fitting')
        for r,yr,fn,om,re,p,b,xl,fix in iter_obj:
            
            # get data for chisq calculations
            x,y,dy = _get_asym(bdata(r,year=yr),asym_mode,rebin=re,omit=om)
            
            # get x limits
            if xl is None:  
                xl = [-np.inf,np.inf]
            else:
                if xl[0] is None: xl[0] = -np.inf
                if xl[1] is None: xl[1] = np.inf
            
            # get good data
            idx = (xl[0]<x)*(x<xl[1])*(dy!=0)
            x = x[idx]
            y = y[idx]
            dy = dy[idx]
            
            # trivial case: all parameters fixed
            if all(fix):
                lenp = len(p)
                s = np.full((lenp,lenp),np.nan)
                c = np.sum(np.square((y-fn(x,*p))/dy))/len(y)
                
            # fit with free parameters
            else:            
                p,s,c = fit_single(r,yr,fn,om,re,hist_select,p0=p,bounds=b,
                                   xlim=xl,asym_mode=asym_mode,fixed=fix,**kwargs)
            # outputs
            pars.append(p)
            covs.append(s)
            chis.append(c)
            
            # get global chi             
            gchi += np.sum(np.square((y-fn(x,*p))/dy))
            dof += len(x)-len(p)
        gchi /= dof
        
    pars = np.asarray(pars)
    covs = np.asarray(covs)
    chis = np.asarray(chis)
            
    return(pars,covs,chis,gchi)

# =========================================================================== #
def fit_single(run,year,fn,omit='',rebin=1,hist_select='',xlim=None,asym_mode='c',
               fixed=None,**kwargs):
    """
        Fit combined asymetry from bdata.
    
        runs:           run number
        
        years:          year
        
        fn:             function handle to fit
        
        omit:           string of space-separated bin ranges to omit
        rebin:          rebinning of data prior to fitting. 
        
        hist_select:    string for selecting histograms to use in asym calc
        
        xlim:           2-tuple for (low,high) bounds on fitting range based on 
                            x values
        
        asym_mode:      input for asymmetry calculation type 
                            c: combined helicity
                            h: split helicity
                            
                        For 2e mode, prefix with:
                            sl_: combined timebins using slopes
                            dif_: combined timebins using differences
                            raw_: raw time-resolved
                            
                            ex: sl_c or raw_h or dif_c
        
        fixed:          list of booleans indicating if the paramter is to be 
                        fixed to p0 value (same length as p0). Returns best 
                        parameters in order presented, with the fixed 
                        parameters omitted.
        
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: (par,cov,chi)
            par: best fit parameters
            cov: covariance matrix
            chi: chisquared of fit
    """
    
    # Get data input
    data = bdata(run,year)
    x,y,dy = _get_asym(data,asym_mode,rebin=rebin,omit=omit)
            
    # check for values with error == 0. Omit these values. 
    tag = dy != 0
    x = x[tag]
    y = y[tag]
    dy = dy[tag]
    
    # apply xlimits
    if xlim is not None:
        tag =(xlim[0]<x)*(x<xlim[1])
        x = x[tag]
        y = y[tag]
        dy = dy[tag]
    
    # p0
    if 'p0' not in kwargs:
        kwargs['p0'] = np.ones(fn.__code__.co_argcount-1)
    
    # fixed parameters
    did_fixed = False
    if fixed is not None and any(fixed):
        
        # save stuff for inflation
        did_fixed = True
        p0 = np.copy(kwargs['p0'])
        npar = len(p0)
        
        # dumb case: all values fixed: 
        if all(fixed):
            cov = np.full((npar,npar),np.nan)
            chi = np.sum(np.square((y-fn(x,*p0))/dy))/len(y)
            return (p0,cov,chi)
        
        # prep inputs
        fixed = np.asarray(fixed)
        if 'bounds' in kwargs:  bounds = kwargs['bounds']
        else:                   bounds = None
        
        # get fixed version
        fn,kwargs['p0'],bounds = _get_fixed_values(fixed,fn,kwargs['p0'],bounds)
        
        # modify fiting inputs
        if bounds is not None:  kwargs['bounds'] = bounds
        
    # Fit the function 
    par,cov = curve_fit(fn,x,y,sigma=dy,absolute_sigma=True,**kwargs)
    dof = len(y)-len(kwargs['p0'])
    
    # get chisquared
    chi = np.sum(np.square((y-fn(x,*par))/dy))/dof
    
    # inflate parameters with fixed values 
    if did_fixed:
        
        # inflate parameters
        par_inflated = np.zeros(npar)
        par_inflated[fixed] = p0[fixed]
        par_inflated[~fixed] = par
        par = par_inflated
        
        # inflate cov matrix with NaN
        nfixed_flat = np.concatenate(np.outer(~fixed,~fixed))
        c_inflated = np.full(npar**2,np.nan)
        c_inflated[nfixed_flat] = np.concatenate(cov)
        cov = c_inflated.reshape(npar,-1)
    
    return (par,cov,chi)
    
# =========================================================================== #
def _get_asym(data,asym_mode,**asym_kwargs):
    """
        Get asymmetry
        
        data = bdata object
        asym_mode: mode as described above
    """
    
    if asym_mode in ('c','p','n','sc','dc','sl_c','dif_c'):
        x,y,dy = data.asym(asym_mode,**asym_kwargs)
    elif asym_mode in ('h','sh','dh','sl_h','dif_h'):
        raise RuntimeError('Split helicity fitting not yet implemented')
    elif 'raw' in asym_mode:
        raise RuntimeError('2e Time-resolved fitting not yet implemented')

    return (x,y,dy)
    
# =========================================================================== #
def _get_fixed_values(fixed,fn,p0,bounds=None):
    """
        Get fixed function, p0, bounds
    """
    
    # save original inputs
    fn_orig = fn
    p0_orig = np.copy(p0)
    npar_orig = len(p0_orig)
            
    # index of fixed parameters
    idx = np.where(fixed)
    
    # make new fitting function with fixed parameter(s)
    def fn(x,*args):
        args_fixed = np.zeros(npar_orig)
        args_fixed[fixed] = p0_orig[fixed]
        args_fixed[~fixed] = args
        return fn_orig(x,*args_fixed)
    
    # make new p0
    p0 = np.asarray(p0_orig)[~fixed]
    
    # bounds
    if bounds is not None:
        try:
            bounds[0] = np.asarray(bounds[0])[~fixed]
            bounds[1] = np.asarray(bounds[1])[~fixed]
        except IndexError:
            pass
    
    return (fn,p0,bounds)
