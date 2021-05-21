# Test constrained fit module
from numpy.testing import *
import numpy as np
from bfit.gui.popup_fit_constraints import popup_fit_constraints
from bfit.gui.bfit import bfit

# filter unneeded warnings
import pytest
pytestmark = pytest.mark.filterwarnings('ignore:2020')

def with_bfit(function):
    
    def wrapper(*args, **kwargs):
        # make gui
        b = bfit(None, True)
        tab = b.fit_files
        tab2 = b.fetch_files
        b.notebook.select(2)
        
        tab2.year.set(2020)
        tab2.run.set('40123 40127')
        tab2.get_data()
        tab.populate()
        b.draw_fit.set(False)
        
        try:
            return function(*args, **kwargs, b=b, fittab=tab, fetchtab=tab2)
        finally:
            b.on_closing()
            del b
            
    return wrapper

@with_bfit
def test_par_detection(b=None, fittab=None, fetchtab=None):
    
    constr = popup_fit_constraints(b)
    constr.entry.insert('1.0', '1_T1 = a*np.exp(b*BIAS**0.5) + c\namp=d')
    constr.get_input()
    
    assert all([k in constr.new_par['name'].values for k in 'abcd'])
    assert len(constr.new_par['name'].values) == 4

@with_bfit
def test_defineable(b=None, fittab=None, fetchtab=None):
    
    constr = popup_fit_constraints(b)
    assert all([k in constr.parnames for k in ('1_T1', 'amp')])
    assert len(constr.parnames) == 2
    
@with_bfit
def test_fit_accuracy(b=None, fittab=None, fetchtab=None):
    
    constr = popup_fit_constraints(b)
    constr.entry.insert('1.0', '1_T1 = a\namp=b')
    constr.get_input()
    constr.do_fit()
    
    # get results
    out_c = constr.new_par.set_index('name')
    
    # fit with normal sharing
    line = fittab.fit_lines['2020.40123']
    entry = line.parentry
    entry['1_T1']['shared'][0].set(True)
    entry['amp']['shared'][0].set(True)
    fittab.do_fit()
    
    # check results
    assert_almost_equal(out_c.loc['a','res'], float(entry['1_T1']['res'][1].get()), 
                        err_msg = 'T1 res not equal', decimal=5)
    assert_almost_equal(out_c.loc['a','err+'], float(entry['1_T1']['dres+'][1].get()), 
                        err_msg = 'T1 err+ not equal', decimal=5)
    assert_almost_equal(out_c.loc['a','err-'], float(entry['1_T1']['dres-'][1].get()), 
                        err_msg = 'T1 err- not equal', decimal=5)
    
    assert_almost_equal(out_c.loc['b','res'], float(entry['amp']['res'][1].get()), 
                        err_msg = 'T1 res not equal', decimal=5)
    assert_almost_equal(out_c.loc['b','err+'], float(entry['amp']['dres+'][1].get()), 
                        err_msg = 'T1 err+ not equal', decimal=5)
    assert_almost_equal(out_c.loc['b','err-'], float(entry['amp']['dres-'][1].get()), 
                        err_msg = 'amp err- not equal', decimal=5)
    
@with_bfit
def test_fit_copy(b=None, fittab=None, fetchtab=None):
    
    constr = popup_fit_constraints(b)
    constr.entry.insert('1.0', '1_T1 = a\namp=b')
    constr.get_input()
    constr.do_fit()
    
    # get results
    out_c = constr.new_par.set_index('name')
    line = fittab.fit_lines['2020.40123']
    entry = line.parentry
    
    # check that results copied to main page properly
    assert_almost_equal(out_c.loc['a','res'], float(entry['1_T1']['res'][1].get()), 
                        err_msg = 'T1 res not equal', decimal=5)
    assert_almost_equal(out_c.loc['a','err+'], float(entry['1_T1']['dres+'][1].get()), 
                        err_msg = 'T1 err+ not equal', decimal=5)
    assert_almost_equal(out_c.loc['a','err-'], float(entry['1_T1']['dres-'][1].get()), 
                        err_msg = 'T1 err- not equal', decimal=5)
    
    assert_almost_equal(out_c.loc['b','res'], float(entry['amp']['res'][1].get()), 
                        err_msg = 'T1 res not equal', decimal=5)
    assert_almost_equal(out_c.loc['b','err+'], float(entry['amp']['dres+'][1].get()), 
                        err_msg = 'T1 err+ not equal', decimal=5)
    assert_almost_equal(out_c.loc['b','err-'], float(entry['amp']['dres-'][1].get()), 
                        err_msg = 'amp err- not equal', decimal=5)
    
@with_bfit
def test_1f_1run(b=None, fittab=None, fetchtab=None):
    """
        Test constraining two variables in a single 1f run to be equal
    """
    
    # get 1f data
    fetchtab.remove_all()
    fetchtab.run.set('40037')
    fetchtab.get_data()
    fittab.n_component.set(2)
    fittab.populate()

    # get constrained functions
    constr = popup_fit_constraints(b)
    constr.entry.insert('1.0', 'fwhm_0 = a\nfwhm_1 = a')
    constr.get_input()
    constr.do_fit()
    
