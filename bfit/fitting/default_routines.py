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
                        '2h':('Exp','Str Exp'),
                        '1f':('Lorentzian','Gaussian'),
                        '1n':('Lorentzian','Gaussian')}
     
    # Define names of fit parameters:
    param_names = {     'Exp'       :('1/T1','amp','baseline'),
                        'Str Exp'   :('1/T1','beta','amp','baseline'),
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
                                    is_shared,  # boolean, share value globally?
                                   )
                              }
                where doptions = {  'omit':str,     # bins to omit in 1F calcs
                                    'rebin':int,    # rebinning factor
                                    'group':int,    # fitting group
                                 }
                                            
            returns dictionary of {run: [[par_names],[par_values],[par_errors],[fitfunction pointers]]}
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
            
            elif self.mode == '1f':    
                par,cov,chi,ftemp = fn(data=dat,omit=doptions['omit'],p0=p0,
                                   bounds=bounds,hist_select=hist_select)
                
            # collect results
            cov = np.sqrt(np.diag(cov))
            parout[dat.run] = [keylist,par,cov,chi,ftemp]
        
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
    def gen_init_par(self,fn_name,ncomp,bdataobj):
        """Generate initial parameters for a given function.
        
            fname: name of function. Should be the same as the param_names keys
            ncomp: number of components
            bdataobj: a bdata object representative of the fitting group. 
            
            Set and return dictionary of initial parameters. 
                {par_name:par_value}
        """
        
        # set pulsed exp fit initial parameters
        if fn_name in ['Exp','Str Exp']:
            t,a,da = bdataobj.asym('c')
            
            # ampltitude average of first 5 bins
            amp = abs(np.mean(a[0:5])/ncomp)
            
            # T1: time after beam off to reach 1/e
            idx = int(bdataobj.ppg.beam_on.mean)
            beam_duration = t[idx]
            amp_beamoff = a[idx]
            target = amp_beamoff/np.exp(1)
            
            t_target = t[np.sum(a>target)]
            T1 = t_target-beam_duration
            
            # baseline: average of last 25% of runs
            base = np.mean(a[int(len(a)*0.75):])
            
            # set values
            par_values = {'amp':(amp,0,np.inf),
                          '1/T1':(T1,0,np.inf),
                          'baseline':(base,-np.inf,np.inf),
                          'beta':(0.5,0,1)}
                         
        # set time integrated fit initial parameters
        elif fn_name in ['Lorentzian','Gaussian']:
            
            f,a,da = bdataobj.asym('c')
            
            # get peak asym value
            amin = min(a[a>0])
            
            peak = f[np.where(a==amin)[0][0]]
            base = np.mean(a[:5])
            height = abs(amin-base)
            width = 2*abs(peak-f[np.where(a<amin+height/2)[0][0]])
            
            # set values
            if fn_name == 'Lorentzian':
                par_values = {'peak':(peak,min(f),max(f)),
                              'width':(width,0,np.inf),
                              'height':(height,0,np.inf),
                              'baseline':(base,-np.inf,np.inf)
                             }
            elif fn_name == 'Gaussian':
                par_values = {'peak':(peak,min(f),max(f)),
                              'sigma':(width,0,np.inf),
                              'height':(height,0,np.inf),
                              'baseline':(base,-np.inf,np.inf)
                              }
        else:
            raise RuntimeError('Bad function name.')
        
        # do multicomponent
        par_values2 = {}
        if ncomp > 1: 
            for c in range(ncomp): 
                for n in par_values.keys():
                    if 'baseline' not in n:
                        par_values2[n+'_%d' % c] = par_values[n]
                    else:
                        par_values2[n] = par_values[n]
        else:
            par_values2 = par_values
            
        return par_values2
        
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
    
