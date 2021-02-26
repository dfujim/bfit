import sys

# functions
# ~ import bfit.test.functions as fn
# ~ fn.test_lorentzian()
# ~ fn.test_bilorentzian()
# ~ fn.test_gaussian()
# ~ fn.test_quadlorentzian()
# ~ fn.test_pulsed_exp()
# ~ fn.test_pulsed_strexp()

# numeric integration
# ~ import bfit.test.numeric_integration as ni
# ~ ni.test_numeric_integration()

# least squares
# ~ import bfit.test.leastsquares as ls
# ~ ls.test_no_errors()
# ~ ls.test_dy()
# ~ ls.test_dx()
# ~ ls.test_dxdy()
# ~ ls.test_dya()
# ~ ls.test_dxa()
# ~ ls.test_dx_dya()
# ~ ls.test_dxa_dy()
# ~ ls.test_dxa_dya()

# minuit
# ~ import bfit.test.minuit as mnt
# ~ mnt.test_start()
# ~ mnt.test_name()
# ~ mnt.test_error()
# ~ mnt.test_limit()
# ~ mnt.test_fix()

# global fitting
# ~ import bfit.test.global_fitter as gf
# ~ gf.test_constructor()
# ~ gf.test_fitting()

# inspect tab
# ~ import bfit.test.tab_fileviewer as tfview
# ~ tfview.test_fetch(40123, 2020, '20')
# ~ tfview.test_fetch(40033, 2020, '1f')
# ~ tfview.test_fetch(40037, 2020, '1w')
# ~ tfview.test_fetch(40011, 2020, '1n')
# ~ tfview.test_fetch(45539, 2019, '2h')
# ~ tfview.test_fetch(40326, 2019, '2e')
# ~ tfview.test_draw(40123, 2020, '20')
# ~ tfview.test_draw(40033, 2020, '1f')
# ~ tfview.test_draw(40037, 2020, '1w')
# ~ tfview.test_draw(40011, 2020, '1n')
# ~ tfview.test_draw(45539, 2019, '2h')
# ~ tfview.test_draw(40326, 2019, '2e')
# ~ tfview.test_autocomplete()
# ~ tfview.test_draw_mode()
# ~ b.do_close_all()

# fetch tab
# ~ import bfit.test.tab_fetch_files as tfetch
# ~ tfetch.test_fetch()
# ~ tfetch.test_remove()
# ~ tfetch.test_checkbox()
# ~ tfetch.test_draw()

# fit tab
import bfit.test.tab_fit_files as tfit
# ~ tfit.test_populate()
# ~ tfit.test_populate_param()
tfit.test_fit(tfit.separate_curve_fit, 'curve_fit')
# ~ tfit.test_fit(tfit.separate_migrad, 'migrad_hesse')
# ~ tfit.test_fit(tfit.separate_minos, 'migrad_minos')
tfit.test_fit_single(tfit.separate_curve_fit, 'curve_fit')
# ~ tfit.test_fit_single(tfit.separate_migrad, 'migrad_hesse')
# ~ tfit.test_fit_single(tfit.separate_minos, 'migrad_minos')
# ~ tfit.test_fixed()
# ~ tfit.test_shared()
# ~ tfit.test_modify_for_all_reset_p0()
# ~ tfit.test_fit_input()
# ~ tfit.test_p0_prior()
# ~ tfit.test_result_as_p0()
############### ~ tfit.test_draw_fit_results()

# calculator nmr rf attenuation
# ~ import bfit.test.calculator_nmr_atten as calc_nmr_atten
# ~ calc_nmr_atten.test_calc()

# calculator nmr B1
# ~ import bfit.test.calculator_nmr_B1 as calc_nmr_b1
# ~ calc_nmr_b1.test_calc()

# calculator nqr B0
# ~ import bfit.test.calculator_nqr_B0 as calc_nqr_b0
# ~ calc_nqr_b0.test_calc()


