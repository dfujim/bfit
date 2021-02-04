import bfit.test.functions as fn
import bfit.test.leastsquares as ls
import bfit.test.minuit as mnt
import bfit.test.global_fitter as gf

# test functions
# ~ fn.test_lorentzian()
# ~ fn.test_bilorentzian()
# ~ fn.test_gaussian()
# ~ fn.test_quadlorentzian()
# ~ fn.test_pulsed_exp()
# ~ fn.test_pulsed_strexp()

# test least squares
# ~ ls.test_no_errors()
# ~ ls.test_dy()
# ~ ls.test_dx()
# ~ ls.test_dxdy()
# ~ ls.test_dya()
# ~ ls.test_dxa()
# ~ ls.test_dx_dya()
# ~ ls.test_dxa_dy()
# ~ ls.test_dxa_dya()

# ~ mnt.test_start()
# ~ mnt.test_name()
# ~ mnt.test_error()
# ~ mnt.test_limit()
# ~ mnt.test_fix()

gf.test_constructor()
g = gf.test_fitting()
