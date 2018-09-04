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
    fn_list = {}
    epsilon = 1e-9  # for fixing parameters

    # ======================================================================= #
    def __init__(self):
        pass
        
    # ======================================================================= #
    def __call__(self,fn_name,ncomp,data_list,hist_select):
        """
            Fitting controller. 
            
            fn_name: name of function to fit
            ncomp : number of components to incude (2 = biexp, for example)
            data_list: list of [[bdata object,pdict,doptions],]
            hist_select: string for selection of histograms
            
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
        fn = self.get_fn(fn_name,ncomp)

        
        # fit each function 
        for data in data_list:
            
            # split data list into parts
            dat = data[0]
            pdict = data[1]
            doptions = data[2]
            
            # get initial parameters
            keylist = self.gen_param_names(fn_name,ncomp)
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
            
            # fit data
            if self.mode == '20':    
                par,cov,chi,ftemp = fn(data=dat,rebin=doptions['rebin'],p0=p0,
                                   bounds=bounds,hist_select=hist_select)
                self.fn_list[dat.run] = ftemp
            
            elif self.mode == '1f':    
                par,cov,chi,ftemp = fn(data=dat,omit=doptions['omit'],p0=p0,
                                   bounds=bounds,hist_select=hist_select)
                self.fn_list[dat.run] = ftemp
                
            # collect results
            cov = np.sqrt(np.diag(cov))
            parout[dat.run] = [keylist,par,cov,chi]
        
        return parout

    # ======================================================================= #
    def gen_param_names(self,fn_name,ncomp):
        """Make a list of the parameter names based on the number of components.
        """
        
        # get names
        names_orig = self.param_names[fn_name]
        
        # special case of one component
        if ncomp == 1: 
            return names_orig
        
        # multicomponent: make copies of everything other than the baselines
        names = []
        for c in range(ncomp): 
            for n in names_orig[:-1]:
                names.append(n+'_%d' % c)
        names.append(names_orig[-1])
        
        return tuple(names)
        
    # ======================================================================= #
    def gen_init_par(self,fn_name,ncomp):
        """Generate initial parameters for a given function.
        
            fname: name of function. Should be the same as the param_names keys
            
            Set and return dictionary of initial parameters,bounds,fixed boolean. 
                {par:(init,bound_lo,bound_hi,fixed)}
        """
        
        # set with constants (should update to something more intelligent later)
        if fn_name == 'Exp':
            par_values = {'amp':(0.5,0,np.inf),
                               'T1':(2,0,np.inf),
                               'baseline':(0,-np.inf,np.inf),
                               }
        elif fn_name == 'Str Exp':
            par_values = {'amp':(0.5,0,np.inf),
                               'T1':(2,0,np.inf),
                               'beta':(0.5,0,1),
                               'baseline':(0,-np.inf,np.inf),
                                }
        elif fn_name == 'Lorentzian':
            par_values = {'peak':(41.26e6,0,np.inf),
                                'width':(5e4,0,np.inf),
                                'height':(0.01,-np.inf,np.inf),
                                'baseline':(0,-np.inf,np.inf)
                                }
        elif fn_name == 'Gaussian':
            par_values = {'mean':(41.26e6,0,np.inf),
                                'sigma':(5e4,0,np.inf),
                                'height':(0.01,-np.inf,np.inf),
                                'baseline':(0,-np.inf,np.inf)
                                }
        else:
            raise RuntimeError('Bad function name.')
        
        # do multicomponent
        if ncomp == 1: 
            self.par_values = par_values
        else:
            for c in range(ncomp): 
                for n in par_values.keys():
                    if 'baseline' not in n:
                        self.par_values[n+'_%d' % c] = par_values[n]
                    else:
                        self.par_values[n] = par_values[n]
        
        return self.par_values

    # ======================================================================= #
    def get_fn(self,fn_name,ncomp):
        """
            Get the fitting function used.
            
                fn_name: string of the function name users will select. 
                ncomp: number of components
            
            Returns python function(x,*pars)
        """
        
        
        # set fitting function
        if fn_name == 'Lorentzian':
            fn =  partial(fscan,mode='lor',ncomp=ncomp)
            self.mode='1f'
        elif fn_name == 'Gaussian':
            fn =  partial(fscan,mode='gaus',ncomp=ncomp)
            self.mode='1f'
        elif fn_name == 'Exp':
            fn =  partial(slr,mode='exp',ncomp=ncomp,offset=True)
            self.mode='20'
        elif fn_name == 'Str Exp':
            fn =  partial(slr,mode='strexp',ncomp=ncomp,offset=True)
            self.mode='20'
        else:
            raise RuntimeError('Fitting function not found.')
    
        return fn
    
