# Wrapper for easy usage of the iminuit Minuit object
# Derek Fujimoto
# Nov 2020

import inspect
import numpy as np
from iminuit import Minuit
from bfit.fitting.leastsquares import LeastSquares

class minuit(Minuit):
    """
        Chi squared minimization for function of best fit using the minuit code
    """
    
    # ====================================================================== #
    def __init__(self, fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, 
                 fn_prime=None, fn_prime_dx=1e-6, name=None, start=None, 
                 error=None, limit=None, fix=None, print_level=1, **kwargs):
        """
            fn: function handle. f(x, a, b, c, ...)
            x:              x data
            y:              y data
            dy:             error in y
            dx:             error in x
            dy_low:         Optional, if error in y is asymmetric. If not none, dy is upper error
            dx_low:         Optional, if error in y is asymmetric. If not none, dx is upper error
            fn_prime:       Optional, function handle for the first derivative of fn. f'(x, a, b, c, ...)
            fn_prime_dx:    Spacing in x to calculate the derivative for default calculation
            name:           Optional sequence of strings. If set, use this for 
            start:          Optional sequence of numbers. Required if the 
                                function takes an array as input or if it has 
                                the form f(x, *pars), and name is not defined. 
                                Default: 1, broadcasted to all inputs
            error           Optional sequence of numbers. Initial step sizes. 
            limit           Optional sequence of limits that restrict the range 
                                format: [[low, high], [low, high], ...]
                                in which a parameter is varied by minuit. 
                                with None, +/- inf used to disable limit
            fix             Optional sequence of booleans. Default: False
            print_level Set the print_level
                            0 is quiet. 
                            1 print out at the end of MIGRAD/HESSE/MINOS. 
                            2 prints debug messages.
                
            kwargs:         passed to Minuit.from_array_func.
                
                To set for parameter "a" one can also assign the following 
                keywords instead of the array inputs
                    
                    a = initial_value
                    error_a = start_error
                    limit_a = (low, high)
                    fix_a = True
        """
        
        # construct least squares object
        ls = LeastSquares(fn = fn, 
                        x = x, 
                        y = y, 
                        dy = dy, 
                        dx = dx, 
                        dy_low = dy_low, 
                        dx_low = dx_low, 
                        fn_prime = fn_prime, 
                        fn_prime_dx = fn_prime_dx)

        # get number of data points
        self.npts = len(x)

        # detect function names
        if name is None:
            
            # get names from code
            name = inspect.getfullargspec(fn).args
            
            # remove self
            if 'self' in name: name.remove('self')
            
            # remove data input
            name = name[1:]
            
            # check for starting parameters
            if start is not None:
                
                # if they don't match assume array input to function
                try:
                    if len(start) != len(name):
                        name = ['x%d' for d in range(len(start))]
                
                # start is a scalar to be broadcasted
                except TypeError:
                    pass
                
            # check for bad input
            else:
                for n in name:
                    if '*' in n:
                        raise RuntimeError("If array input must define name or start")
                    
        # set errordef for least squares minimization
        kwargs['errordef'] = 1
        
        # set starting values, limits, fixed
        is_start = start is not None
        is_error = error is not None
        is_limit = limit is not None
        is_fix   = fix   is not None
        
        keys = kwargs.keys()
        
        # check limit depth 
        if is_start:    broadcast_start = get_depth(start) < 1
        if is_error:    broadcast_error = get_depth(error) < 1
        if is_limit:    broadcast_limit = get_depth(limit) < 2
        if is_fix:      broadcast_fix   = get_depth(fix)   < 1
        
        # iterate parameter names
        for n in name:
            
            # index of name 
            nidx = list(name).index(n)
            
            # start
            if n not in keys:
                
                if is_start:
                    
                    if broadcast_start: kwargs[n] = start
                    else:               kwargs[n] = start[nidx]
                        
                else:
                    kwargs[n] = 1
                    
            # error
            if is_error and 'error_'+n not in keys:
                
                if broadcast_error:     kwargs['error_'+n] = error
                else:                   kwargs['error_'+n] = error[nidx]
                    
            # limit
            if is_limit and 'limit_'+n not in keys:
                
                if broadcast_limit:     kwargs['limit_'+n] = limit
                else:                   kwargs['limit_'+n] = limit[nidx]    
            
            # fix
            if is_fix and 'fix_'+n not in keys:
                
                if broadcast_fix:       kwargs['fix_'+n] = fix
                else:                   kwargs['fix_'+n] = fix[nidx]
                
        # make minuit object
        super().__init__(ls, 
                         use_array_call=True, 
                         name = name, 
                         print_level = print_level,
                         **kwargs)
        
    # ====================================================================== #
    def chi2(self):
        nfixed = sum(self.fixed.values())
        dof = self.npts - self.narg + nfixed
        return self.fval/dof
        
def get_depth(lst, depth=0):
    try: 
        lst[0]
    except (IndexError, TypeError):
        return depth
    else:
        return get_depth(lst[0], depth+1)
        
        
        
        
