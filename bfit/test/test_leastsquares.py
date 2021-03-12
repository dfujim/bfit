# test least squares object
# Derek Fujimoto
# Feb 2021

from bfit.test.testing import *
from bfit.fitting.leastsquares import LeastSquares
import numpy as np

# set up data to test leastsquares object
fn = lambda x, a, b : a*x+b
x = np.arange(0,2)
y = x+1
dy = [1, 2]
dx = [1, 4]
dxl = [1, 8]
dyl = [1, 10]

def test_no_errors():
    ls = LeastSquares(fn, x, y)
    test(0, ls((1,1)), "least squares no errors good parameters")
    test(2, ls((1,2)), "least squares no errors bad parameters")
    
def test_dy():
    ls = LeastSquares(fn, x, y, dy)
    test(0, ls((1,1)), "least squares dy good parameters")
    test(1/4, ls((2,1)), "least squares dy bad parameters")

def test_dx():
    ls = LeastSquares(fn, x, y, dx=dx)
    test(0, ls((1,1)), "least squares dx good parameters")
    test(1/64, ls((2,1)), "least squares dx bad parameters")

def test_dxdy():
    ls = LeastSquares(fn, x, y, dy, dx)
    test(0, ls((1,1)), "least squares dxdy good parameters")
    test(1/(64+4), ls((2,1)), "least squares dxdy bad parameters")

def test_dya():
    ls = LeastSquares(fn, x, y, dy, dy_low=dyl)
    test(0, ls((1,1)), "least squares dy asymmetric good parameters")
    test(1/100, ls((0,1)), "least squares dy asymmetric low parameters")
    test(1/4, ls((2,1)), "least squares dy asymmetric high parameters")

def test_dxa():
    ls = LeastSquares(fn, x, y, dx=dx, dx_low=dxl)
    test(0, ls((1,1)), "least squares dx asymmetric good parameters")
    test(1/144, ls((2,1)), "least squares dx asymmetric bad parameters")

def test_dx_dya():
    ls = LeastSquares(fn, x, y, dy=dy, dx=dx, dy_low=dyl)
    test(0, ls((1,1)), "least squares dx and dy asymmetric good parameters")
    test(4/(100+16), ls((-1,1)), "least squares dx and dy asymmetric low parameters")
    test(1/(4+64), ls((2,1)), "least squares dx and dy asymmetric high parameters")
    
def test_dxa_dy():
    ls = LeastSquares(fn, x, y, dy=dy, dx=dx, dx_low=dxl)
    test(0, ls((1,1)), "least squares dx and dy asymmetric good parameters")
    test(1/(4+144), ls((2,1)), "least squares dy and dx asymmetric bad parameters")
    
def test_dxa_dya():
    ls = LeastSquares(fn, x, y, dy=dy, dx=dx, dy_low=dyl, dx_low=dxl)
    test(0, ls((1,1)), "least squares dx asymmetric and dy asymmetric good parameters")
    test(4/(100+36), ls((-1,1)), "least squares dx asymmetric and dy asymmetric low parameters")
    test(1/(4+144), ls((2,1)), "least squares dx asymmetric and dy asymmetric high parameters")
