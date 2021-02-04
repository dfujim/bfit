# functions to help test
# Derek Fujimoto
# Feb 2021

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

def test_arr(a, b, msg, tol=1e-9):
    if all(abs(a-b) < tol):
        print("Success: Tested %s accurate to a tolerance of %g" % (msg, tol))
    else:
        raise AssertionError(msg + " failed comparison")
