# test minuit object
# Derek Fujimoto
# Feb 2021

from bfit.test.testing import *
from bfit.fitting.minuit import minuit
import numpy as np

# test inputs
fn = lambda x, a, b, c, d, e: a+b+c+d+e+x
fn2 = lambda x, par: a+b+c+d+e+x
x = np.arange(10)
y = x**2

def test_start():
    m = minuit(fn, x, y, start=[1,2,3,4,5])
    test_perfect(m.values['e'], 5, 'minuit start assignment named ')
    
    m = minuit(fn2, x, y, start=[1,2,3,4,5])
    test_perfect(m.values['x4'], 5, 'minuit start assignment unnamed ')
    
    m = minuit(fn, x, y, e=5)
    test_perfect(m.values['e'], 5, 'minuit start assignment single named ')
    
    m = minuit(fn, x, y)
    test_perfect(m.values['e'], 1, 'minuit start default param named')
    
def test_name():
    m = minuit(fn2, x, y, name=['a', 'b', 'c', 'd', 'e'])
    test_perfect(m.values['e'], 1, 'minuit start default param unnamed ')
    test_perfect(m.values['e'], 1, 'minuit name assignment')
    
def test_error():
    m = minuit(fn, x, y, error=[1,2,3,4,5])
    test_perfect(m.errors['e'], 5, 'minuit errors assignment')
    
    m = minuit(fn, x, y, error=5)
    test_perfect(m.errors['e'], 5, 'minuit errors broadcasting')
    
    m = minuit(fn, x, y, error_e=5)
    test_perfect(m.errors['e'], 5, 'minuit errors name single assignment')
    
def test_limit():
    m = minuit(fn, x, y, limit=[[0,1],[0,2],[0,3],[0,4],[0,5]])
    test_perfect(m.limits['e'][1], 5, 'minuit limits assignment')    
    
    m = minuit(fn, x, y, limit=[0,5])
    test_perfect(m.limits['e'][1], 5, 'minuit limits broadcasting')    
    
def test_fix():
    m = minuit(fn, x, y, fix=[True, True, True, True, True])
    test_perfect(m.fixed['e'], True, 'minuit fixed assignment')
    
    m = minuit(fn, x, y, fix=True)
    test_perfect(m.fixed['e'], True, 'minuit fixed broadcasting')
    
    
