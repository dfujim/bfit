# Module Map

Submodules and function signatures (also available from the top-level bfit module): 

* [**`bfit.fitting.functions`**](https://github.com/dfujim/bfit/blob/master/bfit/fitting/functions.py) (base functions module)
    * [`lorentzian(freq, peak, width, amp)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L24-L25)
    * [`bilorentzian(freq, peak, widthA, ampA, widthB, ampB)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L27-L29)
    * [`quadlorentzian(freq, nu_0, nu_q, eta, theta, phi, amp0, amp1, amp2, amp3, fwhm0, fwhm1, fwhm2, fwhm3, I)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L34-L46)
    * [`gaussian(freq, mean, sigma, amp)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L31-L32)
    * `pulsed_exp`
        * constructor: [`pulsed_exp(lifetime, pulse_len)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L65-L69)
        * call: [`pulsed_exp(time, lambda_s, amp)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L84-L85)
    * `pulsed_biexp`
        * constructor: [`pulsed_biexp(lifetime, pulse_len)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L65-L69)
        * call: [`pulsed_biexp(time, lambda_s, lambdab_s, fracb, amp)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L88-L90)
    * `pulsed_strexp`
        * constructor: [`pulsed_strexp(lifetime, pulse_len)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L65-L69)
        * call: [`pulsed_strexp(time, lambda_s, beta, amp)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/functions.py#L93-L94)
        
* [**`bfit.fitting.fit_bdata`** ](https://github.com/dfujim/bfit/blob/master/bfit/fitting/fit_bdata.py) (fitting bdata files module)
    * [`fit_bdata(data, fn, omit=None, rebin=None, shared=None, hist_select='', xlims=None, asym_mode='c', fixed=None, **kwargs)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/fit_bdata.py#L13-L65)

* [**`bfit.fitting.global_fitter`**](https://github.com/dfujim/bfit/blob/master/bfit/fitting/global_fitter.py) (general global fitting)
    * constructor: [`global_fitter(x, y, dy, fn, shared, fixed=None, metadata=None)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/global_fitter.py#L92-L119)
    * [`draw(mode='stack', xlabel='', ylabel='', do_legend=False, labels=None, savefig='', **errorbar_args`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/global_fitter.py#L227-L247)
    * [`fit(**fitargs)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/global_fitter.py#L307-L336)
    * [`get_chi()`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/global_fitter.py#L444-L451)
    * [`get_par()`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/global_fitter.py#L467-L475)

* [**`bfit.fitting.global_bdata_fitter`**](https://github.com/dfujim/bfit/blob/master/bfit/fitting/global_bdata_fitter.py) (global fitting of bdata objects, inherits from `global_fitter`)
    * constructor: [`global_bdata_fitter(data, fn, shared, xlims=None, rebin=1, asym_mode='c', fixed=None)`](https://github.com/dfujim/bfit/blob/82dc3488872e55521e0dd7363e287a0ffb387f8c/bfit/fitting/global_bdata_fitter.py#L14-L38)

# Module Details

The lorentzian and gaussian are standard python functions. The pulsed functions are actually objects. For optimization purposes, they should be first initialized in the following manner: `fn = pulsed_exp(lifetime, pulse_len)` where *lifetime* is the probe lifetime in seconds and *pulse_len* is the duration of beam on in seconds. After which, the initialized object behaves like a normal function and can be used as such. 

Pulsed functions require double exponential intergration provided in the "FastNumericalIntegration_src" directory. This directory also contains the `integration_fns.cpp` and corresponding header file where the fitting functions are defined. These are then externed to the cython module `integrator.pyx`. 
