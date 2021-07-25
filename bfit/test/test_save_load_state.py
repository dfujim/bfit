# test save and load state
from numpy.testing import *
import numpy as np
import pandas as pd
import bdata as bd
from bfit.gui.bfit import bfit
import os

filename = 'test.yaml'

menu     = (('style', 'alpha', 0.1),
            ('hist_select', 'B+,B-,F+,F-'),
            ('label_default', "1000/T (1/K)"),
            ('ppm_reference', 20),
            ('probe_species', 'F20'),
            ('update_period', 2),
            ('thermo_channel', 'B'),
            ('units', '1f', [1, 'TEST_HZ']),
            ('draw_style', 'new'),
            ('draw_fit', False),
            ('draw_ppm', True),
            ('draw_standardized_res', False),
            ('norm_with_param', False),
            ('use_nbm', True),
            ('draw_rel_peak0', False),
            ('minimizer', 'bfit.fitting.fitter_migrad_minos'),
            )
            
fileview = (('year', 2019),
            ('runn', 40123),
            ('is_updating', True),
            ('asym_type', 'Split Helicity'),
            ('rebin', 20),
            )
            
fetch    = (('year', 2019),
            ('run', '40123 40127'),
            ('check_state', False),
            ('check_state_data', False),
            ('check_state_fit', True),
            ('check_state_res', True),
            ('check_rebin', 2),
            ('check_bin_remove', '10-20'),
            ('asym_type', 'Shifted Split'),
            )
            
dataline = (('check_state', True),
            ('label', 'TEST LABEL'),
            ('rebin', 10),
            ('bin_remove', '10 22'),
            )
            
fit      = (('annotation', 'fwhm'),
            ('asym_type', 'Positive Helicity'),
            ('fit_function_title', 'Gaussian'),
            ('n_component', 2),
            ('par_label', 'testlabel'),
            ('set_as_group', True),
            ('set_prior_p0', True),
            ('use_rebin', True),
            ('xaxis', 'baseline'),
            ('yaxis', 'height'),
            ('xlo', '2.5'),
            ('xhi', '8.6'),
            )
            
fitline  = (('parentry', 'baseline', 'p0', 1),
            ('parentry', 'baseline', 'blo', 2),
            ('parentry', 'baseline', 'bhi', 3),
            ('parentry', 'baseline', 'res', 4),
            ('parentry', 'baseline', 'dres+', 5),
            ('parentry', 'baseline', 'dres-', 6),
            ('parentry', 'baseline', 'chi', 7),
            ('parentry', 'height_0', 'fixed', True),
            ('parentry', 'baseline', 'shared', True),
            )
            
deadtime = (('deadtime', 2),
            ('deadtime_switch', True),
            ('deadtime_global', False),
            )
            
datadir  = (('bnqr_data_dir', 'testdir_nqr'),
            )

def setv(obj_top, values):
    
    # get top level object
    obj = getattr(obj_top, values[0])
    
    # set value
    if hasattr(obj, 'set'):
        obj.set(values[1])
    
    # parentry dict
    elif values[0] == 'parentry':
        obj[values[1]][values[2]][0].set(values[3])
    
    # if dict, get dict value
    elif type(obj) is dict: 
        obj[values[1]] = values[2]
            
    # set value
    else:
        setattr(obj_top, values[0], values[1])

def getv(obj_top, values):
    
    # get top level object
    obj = getattr(obj_top, values[0])
    
    # parentry dict
    if values[0] == 'parentry':
        return (obj[values[1]][values[2]][0].get(), values[3])
    
    # if dict, get dict value
    elif type(obj) is dict: 
        return (obj[values[1]], values[2])

    # get value
    elif hasattr(obj, 'get'):
        return (obj.get(), values[1])
            
    # get value
    else:
        return (getattr(obj_top, values[0]), values[1])

def save():
    
    # make gui
    b = bfit(None, True)

    # set menu items -------------------------------------------------------
    for v in menu:
        setv(b, v)
    
    # set fileviewer items ---------------------------------------------------
    tab = b.fileviewer
    for i, v in enumerate(fileview):
        setv(tab, v)
        if i == 1:
            tab.get_data()
            
    # set fetch items --------------------------------------------------------
    tab = b.fetch_files
    for i, v in enumerate(fetch):
        setv(tab, v)
        if i == 1:
            tab.get_data()

    dline = tab.data_lines['2019.40123']
    for v in dataline:
        setv(dline, v)
    
    # set fit items ----------------------------------------------------------
    tab = b.fit_files
    tab.populate()
    tab.do_fit()
    for v in fit:
        setv(tab, v)
        
    tab.populate()
    
    fit_line = tab.fit_lines['2019.40123']
    for v in fitline:
        setv(fit_line, v)
    
    # misc -------------------------------------------------------------------
    
    # deadtime
    for v in deadtime:
        setv(b, v)
    
    # data directory
    for v in datadir:
        setv(b, v)
        
    # save and clean ---------------------------------------------------------
    b.fit_files.save_state(filename)
    b.on_closing()
    del b

def test_load():
    
    # save
    save()
    
    # make gui and load
    b = bfit(None, True)
    b.fit_files.load_state(filename)
    
    # check list
    def check(obj, lst):
        for v in lst:
            read, desired = getv(obj, v)
            try:
                assert read == desired, ('%s\n%s \n\tACTUAL: %s\n\tDESIRED: %s' % \
                    (str(obj), v[:-1], read, desired))
            except AssertionError as err:
                if type(read) != type(desired): 
                    assert str(read) == str(desired), ('%s\n%s \n\tACTUAL: %s\n\tDESIRED: %s' % \
                        (str(obj), v[:-1], read, desired))
                else:
                    raise err from None
    
    # check all the lists
    check(b, menu)
    check(b.fileviewer, fileview)
    check(b.fetch_files, fetch)
    check(b.fetch_files.data_lines['2019.40123'], dataline)
    check(b.fit_files, fit)
    check(b.fit_files.fit_lines['2019.40123'], fitline)
    check(b, deadtime)
    check(b, datadir)
    
    # save and clean ---------------------------------------------------------
    b.on_closing()    
    del b
    os.remove(filename)
    
