# Set up default fitting routines. 
# Derek Fujimoto
# Aug 2018

from bfit.fitting.continuous import fscan
from bfit.fitting.pulsed import slr
from functools import partial
import numpy as np

class fitter(object):

    # needed to tell users what routine this is
    __name__ = 'default'
    
    # Define possible fit functions for given run modes:
    function_names = {  '20':('Exp','Str Exp'),
                        '1f':('Lorentzian','Gaussian'),
                        '1n':('Lorentzian','Gaussian')}
     
    # Define names of fit parameters:
    param_names = {     'Exp'       :('amp','T1','baseline'),
                        'Str Exp'   :('amp','T1','beta','baseline'),
                        'Lorentzian':('peak','width','height','baseline'),
                        'Gaussian'  :('mean','sigma','height','baseline'),}

    # dictionary of initial parameters
    par_values = {}

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
            fn =  partial(fscan,mode='lor',ncomp=ncomp)
            mode='1f'
        elif fn_name == 'Gaussian':
            fn =  partial(fscan,mode='gaus',ncomp=ncomp)
            mode='1f'
        elif fn_name == 'Exp':
            fn =  partial(slr,mode='exp',ncomp=ncomp,offset=True)
            mode='20'
        elif fn_name == 'Str Exp':
            fn =  partial(slr,mode='strexp',ncomp=ncomp,offset=True)
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
            keylist = self.param_names[fn_name]
            p0 = [pdict[k][0] for k in keylist]
            
            # get fitting bounds
            bounds = [[],[]]
            for k in keylist:
                
                # if fixed, set bounds to p0 +/- epsilon
                if pdict[k][3]:
                    p0i = pdict[k][0]
                    bounds[0].append(p0i-self.epsilon)
                    bounds[1].append(p0i+self.epsilon)
            
                # else set to bounds 
                else:
                    bounds[0].append(pdict[k][1])
                    bounds[1].append(pdict[k][2])
            
            # fit slr data
            if mode == '20':    
                par,cov,ftemp = fn(data=dat,rebin=doptions['rebin'],p0=p0,
                                   bounds=bounds)
            elif mode == '1f':    
                par,cov,ftemp = fn(data=dat,omit=doptions['omit'],p0=p0,
                                   bounds=bounds)
            
            # collect results
            cov = np.sqrt(np.diag(cov))
            parout[dat.run] = [keylist,par,cov]
        
        return parout

    # ======================================================================= #
    def gen_init_par(self,fn_name):
        """Generate initial parameters for a given function.
        
            fname: name of function. Should be the same as the param_names keys
            
            Set and return dictionary of initial parameters,bounds,fixed boolean. 
                {par:(init,bound_lo,bound_hi,fixed)}
        """
        
        # set with constants (should update to something more intelligent later)
        if fn_name == 'Exp':
            self.par_values = {'amp':(0.5,0,np.inf,False),
                               'T1':(2,0,np.inf,False),
                               'baseline':(0,-np.inf,np.inf,False),
                               }
        elif fn_name == 'Str Exp':
            self.par_values = {'amp':(0.5,0,np.inf,False),
                               'T1':(2,0,np.inf,False),
                               'beta':(0.5,0,1,False),
                               'baseline':(0,-np.inf,np.inf,False),
                                }
        elif fn_name == 'Lorentzian':
            self.par_values = {'peak':(41.26e6,0,np.inf,False),
                                'width':(5e4,0,np.inf,False),
                                'height':(0.01,-np.inf,np.inf,False),
                                'baseline':(0,-np.inf,np.inf,False)
                                }
        elif fn_name == 'Gaussian':
            self.par_values = {'mean':(41.26e6,0,np.inf,False),
                                'sigma':(5e4,0,np.inf,False),
                                'height':(0.01,-np.inf,np.inf,False),
                                'baseline':(0,-np.inf,np.inf,False)
                                }
        else:
            raise RuntimeError('Bad function name.')
        
        return self.par_values

    # ======================================================================= #
    def get_values(self,fn_name,x,par):
        """
            return points corresponding to fit values
        """
        
    
