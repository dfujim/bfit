# Data object for holding bdata and related file settings for drawing and 
# fitting. 
# Derek Fujimoto
# Nov 2018

from tkinter import *
from bdata import bdata
import bfit
import numpy as np
from bfit.gui.zahersCalculator import current2field

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
            
            fitfnname:  function (str)
            fitfn:      function (function pointer)
            fitpar:     initial parameters {column:{parname:float}} 
                        Columns are fit_files.fitinputtab.collist
            fitpar_var: initial parameters {column:{parname:StringVar}}
            parnames:   parameter names in the order needed by the fit function
            
            drawarg:    drawing arguments for errorbars (dict)
            group:      group number (IntVar)
            rebin:      rebin factor (IntVar)
            mode:       run mode (str)
            omit:       omit bins, 1f only (StringVar)
            check_state:(BooleanVar)    
    """
     
    # ======================================================================= #
    def __init__(self,parentbfit,bd):
        
        self.bfit = parentbfit
        self.bd = bd
        self.mode = bd.mode
        self.run = bd.run
        self.year = bd.year
        self.area = bd.area
    
        self.rebin = IntVar()
        self.group = IntVar()
        self.omit = StringVar()
        self.label = StringVar()
        self.check_state = BooleanVar()
        
        self.fitpar = {}
        
        self.check_state.set(False)
        
        # initialize fitpar with fitinputtab.collist
        for k in ['p0','blo','bhi','res','dres','chi','fixed']:
            self.fitpar[k] = {}
        
        # set temperature 
        try:
            self.temperature = self.bd.camp.smpl_read_A.mean
        except AttributeError:
            self.temperature = self.bd.camp.oven_readC.mean
            
        # field
        try:
            if bd.area == 'BNMR':
                self.field = bd.camp.b_field.mean
                self.field_std = bd.camp.b_field.std
            else:
                self.field = current2field(bd.camp.hh_current.mean)*1e-4
                self.field_std = current2field(bd.camp.hh_current.std)*1e-4
        except AttributeError:
            self.field = -1
            
        # bias
        try:
            if bd.area == 'BNMR': 
                self.bias = bd.epics.nmr_bias_p.mean
                self.bias_std = bd.epics.nmr_bias_p.std
            else:
                self.bias = bd.epics.nqr_bias.mean/1000.
                self.bias_std = bd.epics.nqr_bias.std/1000.
        except AttributeError:
            self.bias = -1

    # ======================================================================= #
    def asym(self,*args,**kwargs):  return self.bd.asym(*args,**kwargs)

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

    # ======================================================================= #
    def set_fitresult(self,values):
        """Set fit results. Values is output of fitting routine. It is 
        dictionary of lists: {run:[parname/par/err/chi/fnpointer]}
        """
        
        self.parnames = values[0]
        
        for i in range(len(self.parnames)):
            key = values[0][i]
            self.fitpar['res'][key] = values[1][i]
            self.fitpar['dres'][key] = values[2][i]
            self.fitpar['chi'][key] = values[3]
        self.chi = values[3]
        self.fitfn = values[4]
        
    # ======================================================================= #
