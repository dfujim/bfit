# Set up default fitting routines. 
# Derek Fujimoto
# Aug 2018

from bfit.fitting.continuous import fscan
from bfit.fitting.pulsed import slr
from functools import partial
import numpy as np

class fitter(object):
    
    # Define possible fit functions for given run modes:
    function_names = {  '20':('Exp','Str Exp'),
                        '1f':('Lorentzian','Gaussian'),
                        '1n':('Lorentzian','Gaussian')}
     
    # Define names of fit parameters:
    param_names = {     'Exp'       :('amp','T1','baseline'),
                        'Str Exp'   :('amp','T1','beta','baseline'),
                        'Lorentzian':('peak','width','height','baseline'),
                        'Gaussian'  :('mean','sigma','height','baseline'),}

    epsilon = 1e-9  # for fixing parameters

    # ======================================================================= #
    def __init__(self):
        pass
    
    # ======================================================================= #
    def __call__(self,fn_name,ncomp,data_list):
        """
            Fitting controller. 
            
            fn_name: name of function to fit
            ncomp : number of components to incude (2 = biexp, for example)
            data_list: list of [[bdata object,pdict,doptions],]
            
                where pdict = {par:(init val,   # initial guess
                                    bound_lo,   # lower fitting bound
                                    bound_hi,   # upper fitting bound
                                    is_fixed,   # boolean, fix value?
                                    is_shared,  # boolean, share globally?
                                   )
                              }
                where doptions = {  'omit':str,     # bins to omit in 1F calcs
                                    'rebin':int,    # rebinning factor
                                    'group':int,    # fitting group
                                 }
                                            
            returns dictionary of {run: [[par_names],[par_values],[par_errors]]}
        """

        # initialize output
        parout = {}

        # set fitting function
        if fn_name == 'Lorentzian':
            fn =  partial(fscan,mode='lor',ncamp=ncomp)
            mode='1f'
        elif fn_name == 'Gaussian':
            fn =  partial(fscan,mode='gaus',ncamp=ncomp)
            mode='1f'
        elif fn_name == 'Exp':
            fn =  partial(slr,mode='exp',ncamp=ncomp,offset=True)
            mode='20'
        elif fn_name == 'Str Exp':
            fn =  partial(slr,mode='strexp',ncamp=ncomp,offset=True)
            mode='20'
        else:
            raise RuntimeError('Fitting function not found.')
        
        # fit each function 
        for data in data_list:
            
            # split data list into parts
            dat = data[0]
            pdict = data[1]
            doptions = data[2]
            
            # get initial parameters
            keylist = list(pdict.keys())
            keylist.sort()
            p0 = [pdict[k][0] for k in keylist]
            
            # get fitting bounds
            bounds = []
            for k in keylist:
                
                # if fixed, set bounds to p0 +/- epsilon
                if pdict[k][3]:
                    p0i = pdict[k][0]
                    bounds.append([p0i-self.epsilon,p0i+self.epsilon])
            
                # else set to bounds 
                else:
                    bounds.append([pdict[k][1],pdict[k][2]])
            
            # fit slr data
            if mode == '20':    
                par,cov,ftemp = fn(data=dat,rebin=doptions['rebin'],p0=p0,
                                   bounds=bounds):
            elif mode == '1f':    
                par,cov,ftemp = fn(data=dat,omit=doptions['omit'],p0=p0,
                                   bounds=bounds):
            
            # collect results
            cov = np.sqrt(np.diag(cov))
            parout[dat.run] = [keylist,par,cov]
        
        return parout
