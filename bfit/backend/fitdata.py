# Data object for holding bdata and related file settings for drawing and 
# fitting. 
# Derek Fujimoto
# Nov 2018

from tkinter import *
from bdata import bdata, bjoined
from bfit.gui.calculator_nqr_B0 import current2field
from bfit import logger_name
from bfit.backend.weighted_mean import wmean, wstd

import numpy as np

import bfit
import logging

# =========================================================================== #
# =========================================================================== #
class fitdata(object):
    """
        Hold bdata and related file settings for drawing and fitting in fetch 
        files tab and fit files tab. 
        
        Data Fields:
            
            bfit:       pointer to top level parent object (bfit)
            bd:         bdata object for data and asymmetry (bdata)
            chi:        chisquared from fit (float)
            run:        run number (int)
            year:       run year (int)
            label:      label for drawing (StringVar)
            field:      magnetic field in T (float)
            field_std:  magnetic field standard deviation in T (float)
            bias:       platform bias in kV (float)
            bias_std:   platform bias in kV (float)
            
            id:         key for unique idenfication (str)    
            fn_title:   function (str)
            fitfn:      function (function pointer)
            fitpar:     initial parameters {column:{parname:float}} and results
                        Columns are fit_files.fitinputtab.collist
            parnames:   parameter names in the order needed by the fit function
            
            drawarg:    drawing arguments for errorbars (dict)
            rebin:      rebin factor (IntVar)
            mode:       run mode (str)
            ncomp:      number of components (int)
            omit:       omit bins, 1f only (StringVar)
            check_state:(BooleanVar)    
    """
     
    # ======================================================================= #
    def __init__(self,parentbfit,bd):
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing run %d (%d).',bd.run,bd.year)
        
        # top level pointer
        self.bfit = parentbfit
        
        # bdata access
        self.bd = bd
        
        # input variables for tkinter
        self.rebin = IntVar()
        self.omit = StringVar()
        self.label = StringVar()
        self.check_state = BooleanVar()
        
        self.check_state.set(False)
        
        # fit parameters dictionary
        self.fitpar = {}
        
        # fit title and comp (set in tab_fit_files)
        self.fit_title = ""
        self.ncomp = -1
        
        # key for IDing file 
        self.id = self.bfit.get_run_key(data=bd)
        
        # initialize fitpar with fitinputtab.collist
        for k in ['p0','blo','bhi','res','dres','chi','fixed','shared']:
            self.fitpar[k] = {}
        
        self.read()

    # ======================================================================= #
    def __getattr__(self,name):
        """Access bdata attributes in the case that fitdata doesn't have it."""
        try:
            return self.__dict__[name]
        except KeyError:
            return getattr(self.bd,name)
    
    # ======================================================================= #
    def asym(self,*args,**kwargs):  return self.bd.asym(*args,**kwargs)

    # ======================================================================= #
    def read(self):
        """Read data file"""
        
        # bdata access
        if type(self.bd) is bdata:
            self.bd = bdata(self.run,self.year)    
        elif type(self.bd) is bjoined:
            self.bd = bjoined([bdata(r,y) for r,y in zip(self.run,self.year)])
            
        # set temperature 
        try:
            self.temperature = wmean(self.bd.camp.smpl_read_A)
            self.temperature_std = wstd(self.bd.camp.smpl_read_A)
        except AttributeError:
            self.logger.exception('Thermometer smpl_read_A not found')
            try:
                self.temperature = wmean(self.bd.camp.oven_readC)
                self.temperature_std = wstd(self.bd.camp.oven_readC)
            except AttributeError:
                self.logger.exception('Thermometer oven_readC not found')
                self.temperature = -1111
                self.temperature_std = -1111
        
        # field
        try:
            if self.bd.area == 'BNMR':
                self.field = wmean(self.bd.camp.b_field)
                self.field_std = wstd(self.bd.camp.b_field)
            else:
                self.field = current2field(wmean(self.bd.epics.hh_current))*1e-4
                self.field_std = current2field(wstd(self.bd.epics.hh_current))*1e-4
        except AttributeError:
            self.logger.exception('Field not found')
            self.field = np.nan
            self.field_std = np.nan
            
        # bias
        try:
            if self.bd.area == 'BNMR': 
                self.bias = wmean(self.bd.epics.nmr_bias)
                self.bias_std = wstd(self.bd.epics.nmr_bias)
            else:
                self.bias = wmean(self.bd.epics.nqr_bias)/1000.
                self.bias_std = wstd(self.bd.epics.nqr_bias)/1000.
        except AttributeError:
            self.logger.exception('Bias not found')
            self.bias = np.nan
            
        # duration 
        try:
            self.duration = int(np.sum(self.bd.duration))
        except AttributeError:
            self.logger.exception('duration not found')
            self.duration = -1111

    # ======================================================================= #
    def set_fitpar(self,values):
        """Set fitting initial parameters
        values: output of routine gen_init_par: 
                {par_name:(par,lobnd,hibnd)}
        """
    
        for v in values.keys():
            self.fitpar['p0'][v] = values[v][0]
            self.fitpar['blo'][v] = values[v][1]
            self.fitpar['bhi'][v] = values[v][2]
        
        self.logger.debug('Fit parameters set to %s',self.fitpar)

    # ======================================================================= #
    def set_fitresult(self,values):
        """
            Set fit results. Values is output of fitting routine. It is a list 
            of tuples
            [(parname),(par),(err),chi,fnpointer]
        """
        self.parnames = values[0]
        
        for i in range(len(self.parnames)):
            key = values[0][i]
            self.fitpar['res'][key] = values[1][i]
            self.fitpar['dres'][key] = values[2][i]
            self.fitpar['chi'][key] = values[3]
        self.chi = values[3]
        self.fitfn = values[4]
        
        self.logger.debug('Setting fit results to %s',self.fitpar)
    
