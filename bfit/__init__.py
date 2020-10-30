import os
import bfit.fitting.functions as functions
import bfit.fitting.fit_bdata as fit_bdata
import bfit.fitting.global_bdata_fitter as global_bdata_fitter
import bfit.fitting.global_fitter as global_fitter

__all__ = ['gui','fitting','backend']
__version__ = '3.6.3'
__author__ = 'Derek Fujimoto'
logger_name = 'bfit'
icon_path = os.path.join(os.path.dirname(__file__),'images','icon.gif')

