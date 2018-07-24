# Fitting BNMR Data

## Compiling Pulsed Functions

First, one should install the fitting functions: `python3 setup_integrator.py build_ext --inplace` 

Stretched exponential fitting requires double exponential intergration provided in the "FastNumericalIntegration_src" directory. This directory also contains the `integration_fns.cpp` and corresponding header file where the fitting functions are defined. These are then externed to the cython module `integrator.pyx`. 

## Fitting Pulsed Functions (SLR)

`from bfit.fitting.pulsed import import slr` 

```text
slr(data,mode,rebin=1,offset=False,ncomp=1,probe='8Li',**kwargs)

    Fit combined asymetry from pulsed beam SLR data: time scan.

    data: tuple of (xdata,ydata,yerr,life,pulse) OR bdata object.

        xdata:  np array of xaxis data to fit.
        ydata:  np array of yaxis data to fit.
        yerr:   np array of error in ydata.
        life:   probe lifetime in s.
        pulse:  duration of beam-on time in s.

    mode:           one of "strexp, mixed_strexp, exp".
    rebin:          rebinning of data prior to fitting. 
    offset:         if True, include offset parameter in fitting function.
                        ensure that p0[-1] = offset, if specified. 
    ncomp:          number of compenents. Ex: for exp+exp set ncomp=2. 
    probe:          string for probe species. Tested only for 8Li. 
    kwargs:         keyword arguments for curve_fit. See curve_fit docs. 

    Returns: par,cov,fn
        par: best fit parameters
        cov: covariance matrix
        fn:  function pointer to fitted function
```

See [curve_fit](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html) documentation for kwargs values. 

Function parameter order on output

| Mode | Parameter Order |
| -------- | -------- |
| exp     | lambda, amp |
| strexp     | lambda, beta, amp |
| mixed_strexp     | lambda1, beta1, lambda2, beta2, alpha, amp |

for `ncomp > 1`, the above order repeats `ncomp` times. If `offset = True`, then the last parameter is the offset. 

## Fitting Frequency Scans (1F)

Simply `from bfit.fitting.continuous import fscan`

```text
fscan(data,mode,omit='',ncomp=1,probe='8Li',**kwargs):

    Fit combined asymetry from 1F run: frequency scan. 

    data: tuple of (xdata,ydata,yerr,life) OR bdata object.
        xdata:  np array of xaxis data to fit.
        ydata:  np array of yaxis data to fit.
        yerr:   np array of error in ydata.
        life:   probe lifetime in s.
    mode:           one of "lor, gauss".
    omit:           string of space-separated bin ranges to omit
    ncomp:          number of compenents. Ex: for exp+exp set ncomp=2. 
    probe:          string for probe species. Tested only for 8Li. 
    kwargs:         keyword arguments for curve_fit. See curve_fit docs. 

    Returns: par,cov,fn
        par: best fit parameters
        cov: covariance matrix
        fn:  function pointer to fitted function

    Note: always fits baseline

```

See [curve_fit](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html) documentation for kwargs values. 

Function parameter order on output

| Mode | Parameter Order |
| -------- | -------- |
| lor     | peak, width, amp |
| gaus     | peak, width, amp |

for `ncomp > 1`, the above order repeats `ncomp` times. The last parameter is always the off-resonance baseline. 