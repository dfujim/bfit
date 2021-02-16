# functions to help test
# Derek Fujimoto
# Feb 2021

from bfit.gui.bfit import bfit
import numpy as np

def test(a, b, msg, tol=1e-9):
    if abs(a-b) < tol:
        print("Success: Tested %s accurate to a tolerance of %g" % (msg, tol))
    else:
        raise AssertionError(msg + ": " + str(a) + ' != ' + str(b))    

def test_perfect(a, b, msg):
    if a == b:
        print("Success: Tested %s" % msg)
    else:
        raise AssertionError(msg + ": " + str(a) + ' != ' + str(b))    

def test_misc(test, msg):
    if test:
        print("Success: Tested %s" % msg)
    else:
        raise AssertionError(msg + ": " + str(test) + " returns False")    

def test_arr(a, b, msg, tol=1e-9):
    if all(abs(np.array(a)-np.array(b)) < tol):
        print("Success: Tested %s accurate to a tolerance of %g" % (msg, tol))
    else:
        print(a)
        print(b)
        raise AssertionError(msg + " failed comparison")

def test_action(action, msg, *args, **kwargs):
    try:
        action(*args, **kwargs)
    except Exception as err:
        raise AssertionError("Failure: %s with error %s" % (msg, err)) from None
    else:
        print("Success: %s " % msg)
    
# make gui
b = bfit(None, True)
