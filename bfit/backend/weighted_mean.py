import numpy as np

# ======================================================================= #
def wmean(x):
    """Weighted mean of bjoined attributes"""
    try:
        return np.average(x.mean,weights=1/x.std**2)
    except ZeroDivisionError:
        return np.mean(x.mean)
    
def wstd(x):
    """error in weighted mean"""
    try:
        return 1/np.sum(1/x.std**2)**0.5
    except ZeroDivisionError:
        return np.std(x.mean)
        
