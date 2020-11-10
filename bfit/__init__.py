import os
from .fitting.functions import lorentzian, bilorentzian, gaussian, quadlorentzian
from .fitting.functions import pulsed_exp, pulsed_strexp, pulsed_biexp
from .fitting.global_fitter import global_fitter
from .fitting.global_bdata_fitter import global_bdata_fitter
from .fitting.fit_bdata import fit_bdata

__all__ = ['gui','fitting','backend']
__version__ = '4.0.2'
__author__ = 'Derek Fujimoto'
logger_name = 'bfit'
icon_path = os.path.join(os.path.dirname(__file__),'images','icon.gif')

__all__.extend(("lorentzian", 
                "bilorentzian", 
                "gaussian", 
                "quadlorentzian",
                "pulsed_exp",
                "pulsed_strexp",
                "pulsed_biexp",
                "global_fitter",
                "global_bdata_fitter",
                "fit_bdata",
                ))
