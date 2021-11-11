# Do Monte Carlo Error propagation
# Derek Fujimoto
# Nov 2021

import numpy as np
import pandas as pd
from scipy.stats import truncnorm
from time import time
from pandarallel import pandarallel
pandarallel.initialize(verbose=0)

def get_mcerror(fn, par, err, n=1e6, bounds=None):
    """
        Propagate errors through a function with the Monte Carlo method
        
        fn: function handle with prototype fn(*par), returns scalar
        par: list of parameters passed to fn
        err: list of errors for each parameter (same length and order)
        n: number of instances in MC error propagation
        bounds: if not None, list of lists: [[low], [high]] MC sampled values 
                are always within bounds
    """
    
    n = int(n)
    
    # get parameters to input
    if bounds is None:
        mc_par = [np.random.normal(loc=p, scale=e, size=n) for p, e in zip(par, err)]    
    else:
    
        # check input
        if len(bounds) != 2: 
            raise RuntimeError("bounds must be list of two lists: [low, high]")
    
        # get parameters
        mc_par = []
        for p, e, blo, bhi in zip(par, err, bounds[0], bounds[1]):
            if blo is None: blo = -np.inf
            if bhi is None: bhi = np.inf
            
            # no bounds, effectively
            if np.isinf(blo) and np.isinf(bhi):
                mc_par.append(np.random.normal(loc=p, scale=e, size=n))
                
            # at least one bound
            else:
                
                # do truncated normal
                if e != 0:
                    blo, bhi = (blo - p) / e, (bhi - p) / e
                    mc_par.append(truncnorm.rvs(blo, bhi, loc=p, scale=e, size=n))
                
                # zero error - return value
                else:
                    mc_par.append(np.ones(n)*p)
        
    # set up data frame
    mc_par = np.array(mc_par).T
    df = pd.DataFrame(mc_par)
    
    # set up new function 
    def fn_new(arg):
        return fn(*arg)
    
    # apply function to input parameters
    t = time()
    fn_df = df.parallel_apply(fn_new, axis='columns')
    print(time()-t)
    
    return fn_df.std()
