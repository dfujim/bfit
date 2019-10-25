# Set up default fitting routines. 
# Derek Fujimoto
# Aug 2018

from bfit.fitting.fit_bdata import fit_list
import bfit.fitting.functions as fns
from bfit.fitting.decay_31mg import fa_31Mg
from functools import partial
import numpy as np
import bdata as bd

class fitter(object):

    # needed to tell users what routine this is
    __name__ = 'default'
    
    # Define possible fit functions for given run modes
    function_names = {  '20':('Exp','Bi Exp','Str Exp'),
                        '2h':('Exp','Bi Exp','Str Exp'),
                        '1f':('Lorentzian','Gaussian','BiLorentzian',),
                        '1w':('Lorentzian','Gaussian','BiLorentzian',),
                        '1n':('Lorentzian','Gaussian','BiLorentzian',),
                        '1e':('Lorentzian','Gaussian','BiLorentzian',),
                        '2e':('Lorentzian','Gaussian','BiLorentzian',)}
     
    # Define names of fit parameters:
    param_names = {     'Exp'       :('1_T1','amp'),
                        'Bi Exp'    :('1_T1','1_T1b','fraction_b','amp'),
                        'Str Exp'   :('1_T1','beta','amp'),
                        'Lorentzian':('peak','width','height','baseline'),
                        'BiLorentzian':('peak','widthA','heightA',
                                               'widthB','heightB','baseline'),
                        'Gaussian'  :('mean','sigma','height','baseline'),}

    # dictionary of initial parameters
    par_values = {}
    fn_list = {}
    epsilon = 1e-9  # for fixing parameters

    # define list of ok run modes 
    valid_asym_modes = ('c','p','n','sl_c','dif_c',)

    # ======================================================================= #
    def __init__(self,probe_species='8Li'):
        """
            probe_species: one of the keys in the bdata.life dictionary.
        """
        
        self.probe_species = probe_species
        
    # ======================================================================= #
    def __call__(self,fn_name,ncomp,data_list,hist_select,asym_mode,xlims):
        """
            Fitting controller. 
            
            fn_name: name of function to fit
            ncomp : number of components to incude (2 = biexp, for example)
            data_list: list of [[bdata object,pdict,doptions],]
            
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
                                 
            hist_select: string for selection of histograms
            asym_mode:  input for asymmetry calculation type 
                            c: combined helicity
                            h: split helicity
                            p: positive helicity
                            n: negative helicity
                            
                        For 2e mode, prefix with:
                            sl_: combined timebins using slopes
                            dif_: combined timebins using differences
                            raw_: raw time-resolved
                            
                            ex: sl_c or raw_h or dif_c
            xlims: fit subrange of x axis
            returns dictionary of {run: [[par_names],[par_values],[par_errors],
                                        [chisquared],[fitfunction pointers]]}
                                   and global chisquared
        """

        # check ncomponents
        if ncomp < 1:
            raise RuntimeError('ncomp needs to be >= 1')
            
        asym_mode = asym_mode.replace('2e_','')
            
        # parameter names
        keylist = self.gen_param_names(fn_name,ncomp)
        npar = len(keylist)
        
        # gather list of data to fit 
        fn = []
        runs = []
        years = []
        p0 = []
        bounds = []
        omit = []
        rebin = []
        sharelist = np.zeros(npar,dtype=bool)
        fixedlist = []
        
        for data in data_list:
            
            # split data list into parts
            dat = data[0]
            pdict = data[1]
            doptions = data[2]
            
            # probe lifetime
            life = bd.life[self.probe_species]
            
            # get fitting function for 20 and 2h
            if dat.mode in ['20','2h']: 
                pulse = dat.get_pulse_s()
                
                # fit function
                fn1 = self.get_fn(fn_name,ncomp,pulse,life)
                
                # add corrections for probe daughters
                if self.probe_species == 'Mg31':
                    fn.append(lambda x,*par : fa_31Mg(x,pulse)*fn1(x,*par))
                else:
                    fn.append(fn1)
                
            # 1f functions
            else:                       
                fn.append(self.get_fn(fn_name,ncomp,-1,life))
            
            # get year and run
            runs.append(dat.run)
            years.append(dat.year)
            
            # get initial parameters
            p0.append(tuple(pdict[k][0] for k in keylist))
            
            # get fitting bounds
            bound = [[],[]]
            shlist = []
            fixed = []
            for k in keylist:
                
                # bounds
                bound[0].append(pdict[k][1])
                bound[1].append(pdict[k][2])
                
                # fixed
                fixed.append(pdict[k][3])    
                    
                # sharelist
                shlist.append(pdict[k][4])
                
            bounds.append(bound)
            fixedlist.append(fixed)
            
            # look for any sharelist
            sharelist += np.array(shlist)
            
            # rebin and omit
            try:
                rebin.append(doptions['rebin'])
            except KeyError:
                rebin.append(1)
                
            try:
                omit.append(doptions['omit'])
            except KeyError:
                omit.append('')                
            
        # fit data
        pars,covs,chis,gchi = fit_list(runs,years,fn,omit,rebin,sharelist,
                                       npar=npar,hist_select=hist_select,p0=p0,
                                       bounds=bounds,asym_mode=asym_mode,
                                       fixed=fixedlist,xlims=xlims)
        stds = [np.sqrt(np.diag(c)) for c in covs]
        
        # collect results
        return ({'.'.join(map(str,(d[0].year,d[0].run))):[keylist,p,s,c,f] \
                    for d,p,s,c,f in zip(data_list,pars,stds,chis,fn)},gchi)

    # ======================================================================= #
    def gen_param_names(self,fn_name,ncomp):
        """
            Make a list of the parameter names based on the number of components.
            
            fn_name: name of function (should match those in param_names)
            ncomp: number of components
            
            return (names)
        """
        
        # get names
        names_orig = self.param_names[fn_name]
        
        # special case of one component
        if ncomp == 1: 
            return names_orig
        
        # multicomponent: make copies of everything other than the baselines
        names = []
        for c in range(ncomp): 
            for n in names_orig:
                if 'base' in n: continue
                names.append(n+'_%d' % c)
                
        if 'base' in names_orig[-1]:
            names.append(names_orig[-1])
        
        return tuple(names)
        
    # ======================================================================= #
    def gen_init_par(self,fn_name,ncomp,bdataobj,asym_mode='combined'):
        """Generate initial parameters for a given function.
        
            fname: name of function. Should be the same as the param_names keys
            ncomp: number of components
            bdataobj: a bdata object representative of the fitting group. 
            asym_mode: what kind of asymmetry to fit
            
            Set and return dictionary of initial parameters. 
                {par_name:par_value}
        """
        
        # asym_mode un-used types 
        if asym_mode in (   'h',           # Split Helicity          
                            'hm',          # Matched Helicity
                            'hs',          # Shifted Split          
                            'cs',          # Shifted Combined      
                            'hp',          # Matched Peak Finding
                            'r',           # Raw Scans            
                            'rhist',       # Raw Histograms          
                            '2e_raw_c',    # Combined Hel Raw       
                            '2e_raw_h',    # Split Hel Raw          
                            '2e_sl_h',     # Split Hel Slopes
                            '2e_dif_h',    # Split Hel Diff           
                            'ad',          # Alpha Diffusion  
                            "at_c",        # Combined Hel (Alpha Tag)
                            "at_h",        # Split Hel (Alpha Tag) 
                            "nat_c",       # Combined Hel (!Alpha Tag)
                            "nat_h",       # Split Hel (!Alpha Tag)
                        ):
            errmsg = "Asymmetry calculation type not implemented for fitting"
            raise RuntimeError(errmsg)
        
        # get asymmetry
        x,a,da = bdataobj.asym(asym_mode)
        
        # set pulsed exp fit initial parameters
        if fn_name in ('Exp','Bi Exp','Str Exp'):
            # ampltitude average of first 5 bins
            amp = abs(np.mean(a[0:5])/ncomp)
            
            # T1: time after beam off to reach 1/e
            idx = int(bdataobj.ppg.beam_on.mean)
            beam_duration = x[idx]
            amp_beamoff = a[idx]
            target = amp_beamoff/np.exp(1)
            
            x_target = x[np.sum(a>target)]
            T1 = abs(x_target-beam_duration)
            
            # bounds and amp
            if asym_mode == 'n':
                amp_bounds = (-np.inf,np.inf)
                amp = -amp
            else:
                amp_bounds = (0,np.inf)
            
            # set values
            par_values = {'amp':(amp,*amp_bounds),
                          '1_T1':(1./T1,0,np.inf),
                          '1_T1b':(10./T1,0,np.inf),
                          'fraction_b':(0.5,0,1),
                          'beta':(0.5,0,1)}
                         
        # set time integrated fit initial parameters
        elif fn_name in ('Lorentzian','Gaussian','BiLorentzian'):
            
            # get peak asym value
            amin = min(a[a!=0])
            
            peak = x[np.where(a==amin)[0][0]]
            base = np.mean(a[:5])
            height = abs(base-amin)
            width = 2*abs(peak-x[np.where(a<amin+height/2)[0][0]])
            
            # bounds
            if asym_mode == 'n':
                height_bounds = (-np.inf,0)
            else:
                height_bounds = (0,np.inf)
            
            # set values
            if fn_name == 'Lorentzian':
                par_values = {'peak':(peak,min(x),max(x)),
                              'width':(width,0,np.inf),
                              'height':(height,*height_bounds),
                              'baseline':(base,-np.inf,np.inf)
                             }
            elif fn_name == 'Gaussian':
                par_values = {'mean':(peak,min(x),max(x)),
                              'sigma':(width,0,np.inf),
                              'height':(height,*height_bounds),
                              'baseline':(base,-np.inf,np.inf)
                              }
            if fn_name == 'BiLorentzian':
                par_values = {'peak':(peak,min(x),max(x)),
                              'widthA':(width,0,np.inf),
                              'heightA':(height,*height_bounds),
                              'widthB':(width,0,np.inf),
                              'heightB':(height,*height_bounds),
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
    def get_fn(self,fn_name,ncomp=1,pulse_len=-1,lifetime=-1):
        """
            Get the fitting function used.
            
                fn_name: string of the function name users will select. 
                ncomp: number of components, ex if 2, then return exp+exp
                pulse_len: duration of beam on in s
                lifetime: lifetime of probe in s
            
            Returns python function(x,*pars)
        """
        
        # set fitting function
        if fn_name == 'Lorentzian':
            fn =  fns.lorentzian
            self.mode=1
        elif fn_name == 'BiLorentzian':
            fn =  fns.bilorentzian
            self.mode=1
        elif fn_name == 'Gaussian':
            fn =  fns.gaussian
            self.mode=1
        elif fn_name == 'Exp':
            fn =  fns.pulsed_exp(lifetime,pulse_len)
            self.mode=2
        elif fn_name == 'Bi Exp':
            fn =  fns.pulsed_biexp(lifetime,pulse_len)
            self.mode=2
        elif fn_name == 'Str Exp':
            fn =  fns.pulsed_strexp(lifetime,pulse_len)
            self.mode=2
        else:
            raise RuntimeError('Fitting function not found.')
        
        # Make final function based on number of components
        fnlist = [fn]*ncomp
        
        if self.mode == 1:
            fnlist.append(lambda x,b: b)
        fn = fns.get_fn_superpos(fnlist)
        
        return fn
        
        
        
        
        
