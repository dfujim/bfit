# Data object for holding bdata and related file settings for drawing and 
# fitting. 
# Derek Fujimoto
# Nov 2018

from tkinter import *
from bdata import bdata,bmerged
from bfit.gui.calculator_nqr_B0 import current2field
from bfit import logger_name

import numpy as np

import bfit
import logging
import textwrap

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
            fitfnname:  function (str)
            fitfn:      function (function pointer)
            fitpar:     initial parameters {column:{parname:float}} and results
                        Columns are fit_files.fitinputtab.collist
            parnames:   parameter names in the order needed by the fit function
            
            drawarg:    drawing arguments for errorbars (dict)
            rebin:      rebin factor (IntVar)
            mode:       run mode (str)
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
        
        # key for IDing file 
        self.id = self.bfit.get_run_key(data=bd)
        
        # initialize fitpar with fitinputtab.collist
        for k in ['p0','blo','bhi','res','dres+','dres-','chi','fixed','shared']:
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
    def get_temperature(self,channel='A'):
        """
            Get the temperature of the run.
            Return (T, std T)
        """
        
        try:
            if channel == 'A':
                T = self.bd.camp['smpl_read_A'].mean
                dT = self.bd.camp['smpl_read_A'].std
            elif channel == 'B':
                T = self.bd.camp['smpl_read_B'].mean
                dT = self.bd.camp['smpl_read_B'].std
            elif channel == '(A+B)/2':
                Ta = self.bd.camp['smpl_read_A'].mean
                Tb = self.bd.camp['smpl_read_B'].mean
                dTa = self.bd.camp['smpl_read_A'].std
                dTb = self.bd.camp['smpl_read_B'].std
                
                T = (Ta+Tb)/2
                dT = ((dTa**2+dTb**2)**0.5)/2
            else:
                raise AttributeError("Missing required temperature channel.")
        
        except KeyError:
            T = np.nan
            dT = np.nan
        
        return (T,dT)
        
    # ======================================================================= #
    def read(self):
        """Read data file"""
        
        # bdata access
        if type(self.bd) is bdata:
            self.bd = bdata(self.run,self.year)
        elif type(self.bd) is bmerged:
            years = list(map(int,textwrap.wrap(str(self.year),4)))
            runs = list(map(int,textwrap.wrap(str(self.run),5)))
            self.bd = bmerged([bdata(r,y) for r,y in zip(runs,years)])
                
        # set temperature 
        try:
            self.temperature = temperature_class(*self.get_temperature(self.bfit.thermo_channel.get()))
        except AttributeError as err:
            self.logger.exception(err)
            try:
                self.temperature = self.bd.camp.oven_readC
            except AttributeError:
                self.logger.exception('Thermometer oven_readC not found')
                self.temperature = -1111
        
        # field
        try:
            if self.bd.area == 'BNMR':
                self.field = self.bd.camp.b_field.mean
                self.field_std = self.bd.camp.b_field.std
            else:
                self.field = current2field(self.bd.epics.hh_current.mean)*1e-4
                self.field_std = current2field(self.bd.epics.hh_current.std)*1e-4
        except AttributeError:
            self.logger.exception('Field not found')
            self.field = np.nan
            self.field_std = np.nan
            
        # bias
        try:
            if self.bd.area == 'BNMR': 
                self.bias = self.bd.epics.nmr_bias.mean
                self.bias_std = self.bd.epics.nmr_bias.std
            else:
                self.bias = self.bd.epics.nqr_bias.mean/1000.
                self.bias_std = self.bd.epics.nqr_bias.std/1000.
        except AttributeError:
            self.logger.exception('Bias not found')
            self.bias = np.nan

    # ======================================================================= #
    def set_fitpar(self,values):
        """Set fitting initial parameters
        values: output of routine gen_init_par: 
                {par_name:(par,lobnd,hibnd)}
        """
    
        self.parnames = list(values.keys())
    
        for v in values.keys():
            self.fitpar['p0'][v] = values[v][0]
            self.fitpar['blo'][v] = values[v][1]
            self.fitpar['bhi'][v] = values[v][2]
            self.fitpar['fixed'][v] = values[v][3]
        
        self.logger.debug('Fit parameters set to %s',self.fitpar)

    # ======================================================================= #
    def set_fitresult(self,values):
        """
            Set fit results. Values is output of fitting routine. It is a list 
            of tuples
            [(parname),(par),(err-),(err+),chi,fnpointer]
        """
        self.parnames = values[0]
        
        for i in range(len(self.parnames)):
            key = values[0][i]
            self.fitpar['res'][key] = values[1][i]
            self.fitpar['dres-'][key] = values[2][i]
            self.fitpar['dres+'][key] = values[3][i]
            self.fitpar['chi'][key] = values[4]
        self.chi = values[4]
        self.fitfn = values[5]
        
        self.logger.debug('Setting fit results to %s',self.fitpar)
    

# ========================================================================== #
class temperature_class(object):
    """
        Emulate storage container for camp variable smpl_read_%
    """
    
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std
    
