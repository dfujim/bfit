# test exporting fit values
from numpy.testing import *
import numpy as np
import pandas as pd
import bdata as bd
from bfit.gui.bfit import bfit
import os

# filter unneeded warnings
import pytest
pytestmark = pytest.mark.filterwarnings('ignore:2020')

# test file name
filename = 'TESTFILE.csv'

def with_bfit(function):
    
    def wrapper(*args, **kwargs):
        # make gui
        b = bfit(None, True)
        tab = b.fetch_files
        tab2 = b.fit_files
        b.notebook.select(2)
        b.draw_fit.set(False)
        
        # get data
        tab.year.set(2020)
        tab.run.set('40123 40127')
        tab.get_data()
        
        # fit
        tab2.populate()
        tab2.do_fit()
        
        # test
        try:
            return function(*args, **kwargs, b=b)
        finally:
            b.on_closing()
            del b
            
    return wrapper

def check_columns(filename):
    
    # load file
    df = pd.read_csv(filename, comment='#')
    
    # check columns
    columns = ['Time (s)', 'asymmetry']
    for c in df.columns:
        assert c in columns
    
    # check column length
    assert len(df.columns) == len(columns)

def check_header(filename, data):
    
    # get header lines
    with open(filename, 'r') as fid:
        lines = fid.readlines()
    lines = [l[1:].strip() for l in lines if l[0] == '#']
    
    # strip labels
    lines = [l.split(':')[-1].strip() if i > 1 else l for i, l in enumerate(lines)]
    lines = [l for l in lines if l]
    
    # split lists
    for i in [6, 7, 8, 9]:
        lines[i] = lines[i].split(', ')
    
    # check id
    assert lines[0] == data.id
    
    # check title
    assert lines[1] == data.title
    
    # check fit function
    assert lines[2] == data.fit_title
    
    # check number components
    assert lines[3] == str(data.ncomp)
    
    # check rebin
    assert lines[4] == str(data.rebin.get())
    
    # check chisquared
    assert_almost_equal(float(lines[5]), data.chi, err_msg="chisquared header copy",
                        decimal=6)
    
    # check param names
    assert_array_equal(lines[6], data.parnames, err_msg='parameter names copy')
    
    # check par values, errors
    for i, name in enumerate(lines[6]):
        assert_almost_equal(float(lines[7][i]), data.fitpar.loc[name, 'res'], 
                            err_msg="Parameter value copy %s" % name)
    
        assert_almost_equal(float(lines[8][i]), data.fitpar.loc[name, 'dres-'], 
                            err_msg="Parameter error- copy %s" % name)
    
        assert_almost_equal(float(lines[9][i]), data.fitpar.loc[name, 'dres+'], 
                            err_msg="Parameter error+ copy %s" % name)

def check_content(filename, data):
        
    # get fit function
    fitfn = data.fitfn
    
    # read file
    df = pd.read_csv(filename, comment='#')
    
    x = df['Time (s)'].values
    y = df['asymmetry'].values
        
    # check content
    testy = fitfn(x, *data.fitpar['res'].values)
    assert_array_almost_equal(y, testy, err_msg='asymmetry content check %s' % filename)
    
@with_bfit
def test_columns(b=None):
    
    # export
    b.fit_files.export_fit(directory='.')
    
    # test
    check_columns('2020_40123_fit.csv')
    check_columns('2020_40127_fit.csv')
    
    # clean
    os.remove('2020_40123_fit.csv')
    os.remove('2020_40127_fit.csv')

@with_bfit
def test_header(b=None):
    
    # export
    b.fit_files.export_fit(directory='.')
    
    # test
    check_header('2020_40123_fit.csv', b.data['2020.40123'])
    check_header('2020_40127_fit.csv', b.data['2020.40127'])
    
    # clean
    os.remove('2020_40123_fit.csv')
    os.remove('2020_40127_fit.csv')
    
@with_bfit
def test_content(b=None):
    
    # export
    b.fit_files.export_fit(directory='.')
    
    # test
    check_content('2020_40123_fit.csv', b.data['2020.40123'])
    check_content('2020_40127_fit.csv', b.data['2020.40127'])
    
    # clean
    os.remove('2020_40123_fit.csv')
    os.remove('2020_40127_fit.csv')
