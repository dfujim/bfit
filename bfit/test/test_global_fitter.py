# test the global fitter 
# Derek Fujimoto
# Feb 2021

from bfit.fitting.global_fitter import global_fitter
from bfit.test.testing import *
import numpy as np

# make data sets to fit
fn = [lambda x, a, b: a*x + b, lambda x, a, b: a*x + b]
x = [np.arange(10), np.arange(10)]
y = [x[0]*5+1, x[1]*5+8]
dy = [np.random.rand(10), np.random.rand(10)]
shared = [True, False]

def test_constructor():
    
    # test function broadcasting
    gf = global_fitter(fn[0], x, y, dy, shared=shared)
    test_perfect(len(gf.fn), 2, "global fitter function broadcasting length")
    test_perfect(gf.fn[0], gf.fn[1], "global fitter function broadcasting id")

    # test n 
    test_perfect(gf.npar, 2, "global fitter number parameter detection")
    test_perfect(gf.nsets, 2, "global fitter number data sets detection")
    
    # test fixed broadcasting
    gf = global_fitter(fn, x, y, dy, shared=shared, fixed=[False, True])
    test_perfect(gf.fixed[0,1], True, "global fitter fixed broadcasting 1")
    test_perfect(gf.fixed[1,1], True, "global fitter fixed broadcasting 2")
    
    gf = global_fitter(fn, x, y, dy, shared=shared, fixed=[[False, True],[False, False]])
    test_perfect(gf.fixed[0,1], True, "global fitter fixed assignment 1")
    test_perfect(gf.fixed[1,1], False, "global fitter fixed assignment 2")
    
def test_fitting():
    
    # test fit algo
    gf = global_fitter(fn, x, y, dy, shared=shared)
    gf.fit(minimiser='trf')
    par, std_l, std_h, cov = gf.get_par()
    test(par[0, 0], par[1, 0], "global fitter curve_fit shared parameter equal")
    test(par[0, 0], 5, "global fitter curve_fit parameter 0 result")
    test(par[0, 1], 1, "global fitter curve_fit parameter 1 result")
    test(par[1, 1], 8, "global fitter curve_fit parameter 2 result")
    
    gf.fit(minimiser='migrad')
    par, std_l, std_h, cov = gf.get_par()
    
    test(par[0, 0], par[1, 0], "global fitter migrad shared parameter equal")
    test(par[0, 0], 5, "global fitter migrad parameter 0 result")
    test(par[0, 1], 1, "global fitter migrad parameter 1 result")
    test(par[1, 1], 8, "global fitter migrad parameter 2 result")
    
    gf.fit(minimiser='minos')
    par, std_l, std_h, cov = gf.get_par()
    
    test(par[0, 0], par[1, 0], "global fitter minos shared parameter equal")
    test(par[0, 0], 5, "global fitter minos parameter 0 result")
    test(par[0, 1], 1, "global fitter minos parameter 1 result")
    test(par[1, 1], 8, "global fitter minos parameter 2 result")
    
    test_perfect(len(gf.par), 3, "global fitter internal flattened parameter array length")
    
    # test with fixed parameter
    gf = global_fitter(fn, x, y, dy, shared=shared, fixed=[False, True])
    gf.fit(minimiser='trf')
    par, std_l, std_h, cov = gf.get_par()
    
    test(par[0, 0], par[1, 0], "global fitter curve_fit shared parameter equal")
    test(par[1, 1], 1, "global fitter curve_fit parameter fixed result")
    
    gf.fit(minimiser='migrad')
    par, std_l, std_h, cov = gf.get_par()
    
    test(par[0, 0], par[1, 0], "global fitter migrad shared parameter equal")
    test(par[1, 1], 1, "global fitter migrad parameter fixed result")
    
    gf.fit(minimiser='minos')
    par, std_l, std_h, cov = gf.get_par()
    
    test(par[0, 0], par[1, 0], "global fitter minos shared parameter equal")
    test(par[1, 1], 1, "global fitter minos parameter fixed result")
    
    test_perfect(len(gf.par), 1, "global fitter internal flattened parameter array length with fixed values")
    
    # test bounds broadcasting
    gf = global_fitter(fn, x, y, dy, shared=shared)
    gf.fit(minimiser='trf', bounds = [10,11])
    par, std_l, std_h, cov = gf.get_par()
    
    par = np.concatenate(par)
    
    if all(10 <= par) and all(par <= 11):
        print('Success: Tested global fitter bounds assignment for format [int int]')
    else:
        raise AssertionError('Failed: global fitter bounds assignment for format [int int]')
    
    gf.fit(minimiser='trf', bounds = [[10,10.5],11])
    par, std_l, std_h, cov = gf.get_par()
    
    if all(10 <= par[:,0]) and all(par[:,0] <= 11) and all(10.5 <= par[:,1]) and all(par[:,1] <= 11):
        print('Success: Tested global fitter bounds assignment for format [list int]')
    else:
        print(par)
        raise AssertionError('Failed: global fitter bounds assignment for format [list int]')
    
    gf.fit(minimiser='trf', bounds = [[10,10.5],[10.1,10.6]])
    par, std_l, std_h, cov = gf.get_par()
    
    if all(10 <= par[:,0]) and all(par[:,0] <= 10.1) and all(10.5 <= par[:,1]) and all(par[:,1] <= 10.6):
        print('Success: Tested global fitter bounds assignment for format [list list]')
    else:
        raise AssertionError('Failed: global fitter bounds assignment for format [list list]')
    
    gf.fit(minimiser='trf', bounds = [[[10,10.5],[10.1,10.6]],[[12,12.5],[12.1,12.6]]])
    par, std_l, std_h, cov = gf.get_par()

    if 10 <= par[0,0] <= 10.1 and 10.5 <= par[0,1] <= 10.6 and \
       10 <= par[1,0] <= 10.1 and 12.5 <= par[1,1] <= 12.6:
        print('Success: Tested global fitter bounds assignment for format [[list list]]')
    else:
        raise AssertionError('Failed: global fitter bounds assignment for format [[list list]]')
    
    # test chi2 calc
    try:
        gf.get_chi()
    except Exception:
        raise AssertionError('Failed: global fitter chisquared calculation error')
    else:
        print('Success: Tested global fitter chisquared calculation to run without error')
