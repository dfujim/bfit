# Set up default fitting routines. 
# Derek Fujimoto
# Aug 2018

import bfit.fitting.functions as fns
from bfit.fitting.decay_31mg import fa_31Mg
from functools import partial
import collections
import numpy as np
import bdata as bd

class fitter(object):
    """
        Fitter base class for default minimizers
    """

    # needed to tell users what routine this is
    __name__ = 'base'
    
    # Define possible fit functions for given run modes
    function_names = {  '20':('Exp','Bi Exp','Str Exp'),
                        '2h':('Exp','Bi Exp','Str Exp'),
                        '1f':('Lorentzian','Gaussian','BiLorentzian','QuadLorentz'),
                        '1w':('Lorentzian','Gaussian','BiLorentzian',),
                        '1n':('Lorentzian','Gaussian','BiLorentzian',),
                        '2e':('Lorentzian','Gaussian','BiLorentzian','QuadLorentz')}
     
    # Define names of fit parameters:
    param_names = {     'Exp'       :('1_T1','amp'),
                        'Bi Exp'    :('1_T1','1_T1b','fraction_b','amp'),
                        'Str Exp'   :('1_T1','beta','amp'),
                        'Lorentzian':('peak','fwhm','height','baseline'),
                        'BiLorentzian':('peak','fwhmA','heightA',
                                               'fwhmB','heightB','baseline'),
                        'QuadLorentz':('nu_0', 'nu_q', 'efgAsym', 'efgTheta', 'efgPhi', 
	                               'amp0', 'amp1', 'amp2', 'amp3', 'fwhm',
                                       'baseline'),
                        'Gaussian'  :('mean','sigma','height','baseline'),}

    # nice parameter names for labels
    pretty_param = {'1_T1':             r'$1 / T_1$ (s$^{-1}$)',
                    'amp':              'Amplitude',
                    'fraction_b':       r'$f_{T_1^{(b)}}$',
                    '1_T1b':            r'$1/T_1^{(b)}$ (s$^{-1}$)',
                    'beta':             r'$\beta$',
                    'fwhm':             'FWHM (%s)',
                    'height':           'Height',
                    'baseline':         'Baseline',
                    'peak':             'Peak (%s)',
                    'fwhmA':            'FWHM$_A$ (%s)',
                    'fwhmB':            'FWHM$_B$ (%s)',
                    'heightA':          'Height$_A$',
                    'heightB':          'Height$_B$',
                    'nu_0':             r'$\nu_0$ (%s)',
                    'nu_q':             r'$\nu_q$ (%s)',
                    'efgAsym':          r'$\eta$',
                    'efgTheta':         r'Principle Axes $\theta$ (rad)',
                    'efgPhi':           r'Principle Axes $\phi$ (rad)',
                    'amp0':             'Amplitude$_0$',
                    'amp1':             'Amplitude$_1$',
                    'amp2':             'Amplitude$_2$',
                    'amp3':             'Amplitude$_3$',
                    'fmwh':             'FWHM (%s)',
                    'mean':             r'$\langle\nu\rangle$ (%s)',
                    'sigma':            r'$\sigma$ (%s)',
                    'Beta-Avg 1/<T1>':  r'$1/\langle T_1\rangle_\beta$ (s$^{-1}$)',
                    'B0 Field (T)':     r'$B_0$ Field (T)',
                    }

    # dictionary of initial parameters
    par_values = {}
    fn_list = {}
    epsilon = 1e-9  # for fixing parameters

    # define list of ok run modes 
    valid_asym_modes = ('c','p','n','sl_c','dif_c',)
    
    # probe species spin numbers
    spin = {'Li8':2,    # radioactive daughters: none
            'Li9':1.5,  # radioactive daughters: Be8
            'Li11':0.5, # radioactive daughters: Be11, He6, Be10 
            'Be11':0.5, # radioactive daughters: none 
            'F20':2,    # radioactive daughters: none
            'Mg31':0.5, # radioactive daughters: Al31, Si31 
            'Mg29':1.5, # radioactive daughters: Al29
            'Ac230':1,  # radioactive daughters: none
            'Ac232':1,  # radioactive daughters: unknown
            'Ac234':1,  # radioactive daughters: unkonwn
            }

    # ======================================================================= #
    def __init__(self, keyfn, probe_species='Li8'):
        """
            keyfn:          function takes as input bdata or bjoined object, 
                            returns string corresponding to unique id of that 
                            object
            probe_species: one of the keys in the bdata.life dictionary.
        """
        self.keyfn = keyfn
        self.probe_species = probe_species
        
    # ======================================================================= #
    def __call__(self, fn_name, ncomp, data_list, hist_select, asym_mode, xlims):
        """
            Fitting controller. 
            
            fn_name: name of function to fit
            ncomp : number of components to incude (2 = biexp, for example)
            data_list: list of [[bdata object, pdict, doptions],]
            
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
            returns dictionary of {runid: [[par_names],[par_values],[par_errors],
                                          [chisquared],[fitfunction pointers]]}
                                   and global chisquared
        """

        # check ncomponents
        if ncomp < 1:
            raise RuntimeError('ncomp needs to be >= 1')
            
        asym_mode = asym_mode.replace('2e_','')
            
        # parameter names
        keylist = self.gen_param_names(fn_name, ncomp)
        npar = len(keylist)
        
        # gather list of data to fit 
        fn = []
        bdata_list = []
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
            
            # get bdata objects
            bdata_list.append(dat)
            
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
        kwargs = {'p0':p0, 'bounds':bounds}
        pars, stds_l, stds_h, covs, chis, gchi = self._do_fit(
                                        bdata_list,
                                        fn,
                                        omit,
                                        rebin,
                                        sharelist,
                                        hist_select=hist_select,
                                        asym_mode=asym_mode,
                                        fixed=fixedlist,
                                        xlims=xlims,
                                        parnames=keylist,
                                        **kwargs)
        
        # collect results
        if not isinstance(chis,collections.Iterable):   # single run
            d = bdata_list[0]
            return ({self.keyfn(d):[keylist, pars, stds_l, stds_h, chis, fn[0]]}, gchi)
        else:                                           # multiple runs    
            return ({self.keyfn(d):[keylist, p, sl, sh, c, f] 
                for d, p, sl, sh, c, f in zip(bdata_list, pars, stds_l, stds_h, chis, fn)}, gchi)

    # ======================================================================= #
    def gen_param_names(self, fn_name, ncomp):
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
    def gen_init_par(self, fn_name, ncomp, bdataobj, asym_mode='combined'):
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
            par_values = {'amp':(amp,*amp_bounds,False),
                          '1_T1':(1./T1,0,np.inf,False),
                          '1_T1b':(10./T1,0,np.inf,False),
                          'fraction_b':(0.5,0,1,False),
                          'beta':(0.5,0,1,False)}
                         
        # set time integrated fit initial parameters
        elif fn_name in ('Lorentzian','Gaussian','BiLorentzian','QuadLorentz'):
            
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
            
            # set values (value, low bnd, high bnd, fixed)
            if fn_name == 'Lorentzian':	
                par_values = {'peak':(peak,min(x),max(x),False),
                              'fwhm':(width,0,np.inf,False),
                              'height':(height,*height_bounds,False),
                              'baseline':(base,-np.inf,np.inf,False)
                             }
            elif fn_name == 'Gaussian':
                par_values = {'mean':(peak,min(x),max(x),False),
                              'sigma':(width,0,np.inf,False),
                              'height':(height,*height_bounds,False),
                              'baseline':(base,-np.inf,np.inf,False)
                              }
            elif fn_name == 'BiLorentzian':
                par_values = {'peak':(peak,min(x),max(x),False),
                              'fwhmA':(width*10,0,np.inf,False),
                              'heightA':(height/10,*height_bounds,False),
                              'fwhmB':(width,0,np.inf,False),
                              'heightB':(height*9/10,*height_bounds,False),
                              'baseline':(base,-np.inf,np.inf,False)
                             }
            elif fn_name == 'QuadLorentz':
                
                dx = max(x)-min(x)
                par_values = {'nu_0':((max(x)+min(x))/2,min(x),max(x),False),
                              'nu_q':(dx/12,0,dx,False),
                              'efgAsym':(0,0,1,True),
                              'efgTheta':(0,0,2*np.pi,True),
                              'efgPhi':(0,0,2*np.pi,True),
                              'amp0':(height,height*0.1,np.inf,False), 
                              'amp1':(height,height*0.1,np.inf,False), 
                              'amp2':(height,height*0.1,np.inf,False), 
                              'amp3':(height,height*0.1,np.inf,False), 
                              'fwhm':(dx/10,0,dx,False),
                              'baseline':(base,-np.inf,np.inf,False)
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
    def get_fn(self, fn_name, ncomp=1, pulse_len=-1, lifetime=-1):
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
        elif fn_name == 'QuadLorentz':
            fn =  lambda freq, nu_0, nu_q, eta, theta, phi, \
            		amp0, amp1, amp2, amp3, fwhm: \
                   	fns.quadlorentzian(freq, nu_0, nu_q, eta, theta, phi, \
		            		amp0, amp1, amp2, amp3, \
                		   	fwhm, fwhm, fwhm, fwhm, \
                		   	I=self.spin[self.probe_species])
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
        
        
        
        
        
