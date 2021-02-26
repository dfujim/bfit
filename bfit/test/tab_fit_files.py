# test inspect tab
# Derek Fujimoto
# Feb 2021

from bfit.test.testing import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import bdata as bd
from bfit import pulsed_exp, minuit
from bfit.fitting.leastsquares import LeastSquares

# get bfit object and tab
tab = b.fit_files
tab2 = b.fetch_files
b.notebook.select(2)

def get_data():
    
    # clear setup
    b.do_close_all()
    tab2.remove_all()
    
    # fetch
    tab2.year.set(2020)
    tab2.run.set('40123 40127')
    tab2.get_data()

def test_populate():

    get_data()
    
    # check populate
    tab.populate()
    test_misc('2020.40123' in tab.fit_lines.keys(), 'First fetched run populated')
    test_misc('2020.40127' in tab.fit_lines.keys(), 'Second fetched run populated')
    
    # remove
    tab2.data_lines['2020.40123'].degrid()
    tab.populate()
    test_misc('2020.40123' not in tab.fit_lines.keys(), 'First fetched run removed')
    
    # fetch again
    tab2.get_data()
    tab.populate()
    test_misc('2020.40123' in tab.fit_lines.keys(), 'Re-populated after run removal and refetch')
    
def test_populate_param():
        
    get_data()
    tab.populate()
        
    # get fit line
    line = tab.fit_lines['2020.40123']
    
    # set fit fn
    tab.fit_function_title.set('Str Exp')
    tab.populate_param()
    test_perfect(line.get_new_parameters(), ('1_T1', 'amp', 'beta'), 'Single function parameters populated')
    
    # multiple terms
    tab.fit_function_title.set('Exp')
    tab.n_component.set(2)
    tab.populate_param()
    test_perfect(line.get_new_parameters(), ('1_T1_0', '1_T1_1', 'amp_0', 'amp_1'), 
                 'Two term function parameters populated')
    
# do the fit separately
def separate_curve_fit(entry, run, **kwargs):
    
    # data
    year, run = tuple(map(int, run.split('.')))
    dat = bd.bdata(run, year)
    
    # fit function
    pexp = pulsed_exp(lifetime = bd.life.Li8, pulse_len = dat.get_pulse_s())

    p0 = [float(entry[k]['p0'][1].get()) for k in entry.keys()]
    blo = [float(entry[k]['blo'][1].get()) for k in entry.keys()]
    bhi = [float(entry[k]['bhi'][1].get()) for k in entry.keys()]
    
    # fit
    t,a,da = dat.asym('c')
    par, cov = curve_fit(pexp, t, a, sigma=da, absolute_sigma=True, p0=p0, 
                         bounds=[blo, bhi], **kwargs)
    std = np.diag(cov)**0.5
    
    # chi2
    chi = np.sum(((a-pexp(t, *par))/da)**2)/(len(a)-2)
    
    return (par, std, std, chi)

def separate_migrad(entry, run, do_minos=False, **kwargs):
    
    # data
    year, run = tuple(map(int, run.split('.')))
    dat = bd.bdata(run, year)
    
    # fit function
    pexp = pulsed_exp(lifetime = bd.life.Li8, pulse_len = dat.get_pulse_s())

    # get p0, bounds
    p0 = {k.replace('1_T1','lambda_s'):float(entry[k]['p0'][1].get()) for k in entry.keys()}
    bounds = [( float(entry[k]['blo'][1].get()), 
                float(entry[k]['bhi'][1].get())) for k in entry.keys()]
    
    # fit
    t,a,da = dat.asym('c')
    m = minuit(pexp, t, a, da, **p0, limit = bounds, **kwargs)
    m.migrad()
    
    if do_minos: m.minos()
    
    par = m.values
    
    if do_minos: 
        n = len(par)
        lower = np.abs(np.array([m.merrors[i].lower for i in range(n)]))
        upper = np.array([m.merrors[i].upper for i in range(n)])
    else:
        lower = m.errors
        upper = lower
        
    chi = m.fval
        
    return (par, lower, upper, chi)

def separate_minos(entry, run, **kwargs):
    return separate_migrad(entry, run, do_minos=True, **kwargs)
    
def test_fit(separate_fit, minimizer):
    
    # get data
    get_data()
    tab.populate()
    
    # set minimizer
    b.minimizer.set('bfit.fitting.fitter_%s' % minimizer)
    b.set_fit_routine()
    
    # do fit in bfit
    tab.do_fit()
    
    # check return values -----------------------------------------------------
    
    for k, line in tab.fit_lines.items():
    
        entry = line.parentry
        
        # get results separately
        par, lower, upper, chi2 = separate_fit(entry, k)    
        
        # get results displayed
        res = [float(entry[k]['res'][1].get()) for k in entry.keys()]
        low = [float(entry[k]['dres-'][1].get()) for k in entry.keys()]
        upp = [float(entry[k]['dres+'][1].get()) for k in entry.keys()]
        
        # check
        test_arr(par, res, 'Copying %s minimizer results for %s' % (minimizer, k), tol=1e-3)
        test_arr(lower, low, 'Copying %s minimizer lower errors for %s' % (minimizer, k), tol=1e-3)
        test_arr(upper, upp, 'Copying %s minimizer upper errors for %s' % (minimizer, k), tol=1e-3)
        
        # check chi2
        chi = float(entry['1_T1']['chi'][1].get())
        test(chi, chi2, 'Copying chi2 for %s minimizer for %s' % (minimizer, k), tol=1e-2)
    
    # reset minimizer
    b.minimizer.set('bfit.fitting.fitter_curve_fit')
    b.set_fit_routine()

def test_fit_single(separate_fit, minimizer):
    
    # clear setup
    b.do_close_all()
    tab2.remove_all()
    
    # fetch
    tab2.year.set(2020)
    tab2.run.set('40123')
    tab2.get_data()

    tab.populate()
    line = tab.fit_lines['2020.40123']
    entry = line.parentry
    
    # set minimizer
    b.minimizer.set('bfit.fitting.fitter_%s' % minimizer)
    b.set_fit_routine()
    
    # check return value ------------------------------------------------------
    
    # get results separately
    par, lower, upper, chi2 = separate_fit(entry, '2020.40123')    
    tab.do_fit()
    
    # get results displayed
    res = [float(entry[k]['res'][1].get()) for k in entry.keys()]
    low = [float(entry[k]['dres-'][1].get()) for k in entry.keys()]
    upp = [float(entry[k]['dres+'][1].get()) for k in entry.keys()]
    
    # check
    test_arr(par, res, 'Copying %s minimizer results for single run' % minimizer, tol=1e-3)
    test_arr(lower, low, 'Copying %s minimizer lower errors for single run' % minimizer, tol=1e-3)
    test_arr(upper, upp, 'Copying %s minimizer upper errors for single run' % minimizer, tol=1e-3)
    
    # check chi2
    chi = float(entry['1_T1']['chi'][1].get())
    test(chi, chi2, 'Copying chi2 for %s minimizer for single run' % minimizer, tol=1e-2)
    
    # reset minimizer
    b.minimizer.set('bfit.fitting.fitter_curve_fit')
    b.set_fit_routine()

def test_fit_input():
        
    # get data
    get_data()
    
    # set rebin
    tab2.data_lines['2020.40123'].rebin.set(10)
    tab2.data_lines['2020.40127'].rebin.set(2)
    tab.use_rebin.set(True)
    
    # set function
    tab.fit_function_title.set('Bi Exp')
    
    # set ncomp
    tab.n_component.set(2)
    
    # fit
    tab.populate()    
    tab.do_fit()
    
    # fit input: fn_name, ncomp, data_list
    # data_list: [bdfit, pdict, doptions]
    
    # check function
    test_perfect(tab.fit_input[0], 'Bi Exp', "Function name passing to fitter")
    
    # check ncomp
    test_perfect(tab.fit_input[1], 2, "Number of components passing to fitter")
    
    # check
    test_perfect(tab.fit_input[2][0][2]['rebin'], 10, "Rebin passing for file 1")
    test_perfect(tab.fit_input[2][1][2]['rebin'], 2, "Rebin passing for file 2")

def test_fixed():
    
    # get data
    get_data()
    tab.populate()
    line = tab.fit_lines['2020.40123']
    entry = line.parentry
    
    # fixed input -----------------------------------------------------------
    entry['1_T1']['p0'][0].set('1')
    entry['1_T1']['fixed'][0].set(True)
    tab.do_fit()
    
    test(float(entry['1_T1']['res'][1].get()), 1, 'Fixed result')
    test_misc(np.isnan(float(entry['1_T1']['dres-'][1].get())), 'Fixed lower error')
    test_misc(np.isnan(float(entry['1_T1']['dres+'][1].get())), 'Fixed upper error')
    test_misc(float(entry['amp']['res'][1].get()) != 1, 'Unfixed result')
    test_misc(not np.isnan(float(entry['amp']['dres-'][1].get())), 'Unfixed lower error')
    test_misc(not np.isnan(float(entry['amp']['dres+'][1].get())), 'Unfixed upper error')
    
    # unfix
    entry['1_T1']['fixed'][0].set(False)
   
def test_shared():
    
    # get data
    get_data()
    tab.populate()
    line = tab.fit_lines['2020.40123']
    line2 = tab.fit_lines['2020.40127']
    entry = line.parentry
    entry2 = line2.parentry
    
    # shared input
    entry['1_T1']['shared'][0].set(True)
    tab.do_fit()
    
    T11 = float(entry['1_T1']['res'][1].get())
    T12 = float(entry2['1_T1']['res'][1].get())
    
    test(T11, T12, 'Shared result equal')
    
    T11 = float(entry['1_T1']['dres-'][1].get())
    T12 = float(entry2['1_T1']['dres-'][1].get())
    
    test(T11, T12, 'Shared lower error equal')
    
    T11 = float(entry['1_T1']['dres+'][1].get())
    T12 = float(entry2['1_T1']['dres+'][1].get())
    
    test(T11, T12, 'Shared upper error equal')
    
    # check the unshared result
    amp1 = float(entry['amp']['res'][1].get())
    amp2 = float(entry2['amp']['res'][1].get())
    
    test_misc(amp1 != amp2, 'Unshared result not equal')
    
    amp1 = float(entry['amp']['dres-'][1].get())
    amp2 = float(entry2['amp']['dres-'][1].get())
    
    test_misc(amp1 != amp2, 'Unshared lower error not equal')
    
    amp1 = float(entry['amp']['dres+'][1].get())
    amp2 = float(entry2['amp']['dres+'][1].get())
    
    test_misc(amp1 != amp2, 'Unshared upper error not equal')
    
    # unshare
    entry['1_T1']['shared'][0].set(False)
    
def test_modify_for_all_reset_p0():
    
    # get data
    get_data()
    tab.populate()
    line = tab.fit_lines['2020.40123']
    line2 = tab.fit_lines['2020.40127']
    entry = line.parentry
    entry2 = line2.parentry
    
    # modify
    tab.set_as_group.set(True)
    
    initial = {}
    for k in entry.keys():    
        initial[k] = {}
        for c in ('p0', 'blo', 'bhi'):
            
            initial[k][c] = entry[k][c][0].get()
            entry[k][c][0].set(c)
            test_perfect(entry2[k][c][0].get(), c, "Modify all for %s (%s)" % (k,c))
     
    # reset
    tab.do_reset_initial()
    
    for k in entry.keys():    
        for c in ('p0', 'blo', 'bhi'):
            test_perfect(entry[k][c][0].get(), initial[k][c], "Reset p0 for %s (%s)" % (k,c))
                
def test_p0_prior():
    
    # get data
    get_data()
    tab.populate()
    
    # fit
    tab.do_fit()
    b.do_close_all()
    
    # set next p0
    tab.set_prior_p0.set(True)
    
    # get more data
    tab2.run.set('40124')
    tab2.get_data()
    tab.populate()
    
    # get results and compare
    result = tab.fit_lines['2020.40127'].parentry
    p0 = tab.fit_lines['2020.40124'].parentry
    
    for k in result.keys():
        test(float(result[k]['res'][0].get()), float(p0[k]['p0'][0].get()), 
             'Set last result as p0 for new run for %s'%k, tol=1e-5)
    
def test_result_as_p0():
    
    # get data
    get_data()
    tab.populate()
    
    # fit
    tab.do_fit()
    b.do_close_all()
    
    # set result as P0
    tab.do_set_result_as_initial()
    
    # check
    for run_id in tab.fit_lines.keys():
        entry = tab.fit_lines[run_id].parentry
    
        for k in entry.keys():
            test(float(entry[k]['res'][0].get()), float(entry[k]['p0'][0].get()), 
                'Set result as p0 for %s'%k, tol=1e-5)
        
def test_draw_fit_results():
    pass


