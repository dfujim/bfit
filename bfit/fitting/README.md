# Module Map

Submodules and function signatures (also available from the top-level bfit module): 

* [**`bfit.fitting.functions`**](https://github.com/dfujim/bfit/blob/master/bfit/fitting/functions.py) (base functions module)
    * [`lorentzian(freq, peak, fwhm, amp)`](https://github.com/dfujim/bfit/blob/54ae5717abb7e651780d3bff9c5aae45b4429ee6/bfit/fitting/functions.py#L24-L25)
    * [`bilorentzian(freq, peak, fwhmA, ampA, fwhmB, ampB)`](https://github.com/dfujim/bfit/blob/54ae5717abb7e651780d3bff9c5aae45b4429ee6/bfit/fitting/functions.py#L27-L29)
    * [`quadlorentzian(freq, nu_0, nu_q, eta, theta, phi, amp0, amp1, amp2, amp3, fwhm0, fwhm1, fwhm2, fwhm3, I)`](https://github.com/dfujim/bfit/blob/54ae5717abb7e651780d3bff9c5aae45b4429ee6/bfit/fitting/functions.py#L34-L46)
    * [`gaussian(freq, mean, sigma, amp)`](https://github.com/dfujim/bfit/blob/54ae5717abb7e651780d3bff9c5aae45b4429ee6/bfit/fitting/functions.py#L31-L32)
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
    * [`fit_bdata(data, fn, omit=None, rebin=None, shared=None, hist_select='', xlims=None, asym_mode='c', fixed=None, minimizer='migrad+minos', **kwargs)`](https://github.com/dfujim/bfit/blob/7ef409124b1790b9df04f68407ecf9f26b20a434/bfit/fitting/fit_bdata.py#L16-L72)

* [**`bfit.fitting.global_fitter`**](https://github.com/dfujim/bfit/blob/master/bfit/fitting/global_fitter.py) (general global fitting)
    * constructor: [`global_fitter(fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, shared=None, fixed=None, metadata=None, fprime_dx=1e-6)`](https://github.com/dfujim/bfit/blob/7ef409124b1790b9df04f68407ecf9f26b20a434/bfit/fitting/global_fitter.py#L108-L142)
    * [`draw(mode='stack', xlabel='', ylabel='', do_legend=False, labels=None, savefig='', **errorbar_args`](https://github.com/dfujim/bfit/blob/7ef409124b1790b9df04f68407ecf9f26b20a434/bfit/fitting/global_fitter.py#L376-L396)
    * [`fit(minimizer='migrad', do_minos=True, **fitargs)`](https://github.com/dfujim/bfit/blob/7ef409124b1790b9df04f68407ecf9f26b20a434/bfit/fitting/global_fitter.py#L476-L509)
    * [`get_chi()`](https://github.com/dfujim/bfit/blob/7ef409124b1790b9df04f68407ecf9f26b20a434/bfit/fitting/global_fitter.py#L644-L651)
    * [`get_par()`](https://github.com/dfujim/bfit/blob/7ef409124b1790b9df04f68407ecf9f26b20a434/bfit/fitting/global_fitter.py#L697-L711)

* [**`bfit.fitting.global_bdata_fitter`**](https://github.com/dfujim/bfit/blob/master/bfit/fitting/global_bdata_fitter.py) (global fitting of bdata objects, inherits from `global_fitter`)
    * constructor: [`global_bdata_fitter(data, fn, xlims=None, rebin=1, asym_mode='c', **kwargs)`](https://github.com/dfujim/bfit/blob/7ef409124b1790b9df04f68407ecf9f26b20a434/bfit/fitting/global_bdata_fitter.py#L14-L36)

* [**`bfit.fitting.minuit`**](https://github.com/dfujim/bfit/blob/master/bfit/fitting/minuit.py) (use migrad minimizer for fitting, inherits from [`iminuit.Minuit`](https://iminuit.readthedocs.io/en/stable/reference.html))
    * constructor: [`minuit(fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, fn_prime=None, fn_prime_dx=1e-6, name=None, start=None, error=None, limit=None, fix=None, print_level=1, **kwargs)`](https://github.com/dfujim/bfit/blob/c2a00b730ac64c341b6a9230429b9695ac9e97a1/bfit/fitting/minuit.py#L16-L55)
    * [`chi2()`](https://github.com/dfujim/bfit/blob/c2a00b730ac64c341b6a9230429b9695ac9e97a1/bfit/fitting/minuit.py#L162-L163)
    * Some useful functions (See [`iminuit`](https://iminuit.readthedocs.io/en/stable/reference.html) reference for full documenation): 
        * [`migrad(ncall=None, resume=True, precision=None, iterate=5)`](https://iminuit.readthedocs.io/en/stable/reference.html#iminuit.Minuit.migrad)
        * [`hesse(ncall=None)`](https://iminuit.readthedocs.io/en/stable/reference.html#iminuit.Minuit.hesse)
        * [`minos(var=None, sigma=1., ncall=None)`](https://iminuit.readthedocs.io/en/stable/reference.html#iminuit.Minuit.minos)
        * [`np_values()`](https://iminuit.readthedocs.io/en/stable/reference.html#iminuit.Minuit.np_values)
        * [`np_errors()`](https://iminuit.readthedocs.io/en/stable/reference.html#iminuit.Minuit.np_errors)
        * [`np_merrors()`](https://iminuit.readthedocs.io/en/stable/reference.html#iminuit.Minuit.np_merrors)

# Module Details

The lorentzian and gaussian are standard python functions. The pulsed functions are actually objects. For optimization purposes, they should be first initialized in the following manner: `fn = pulsed_exp(lifetime, pulse_len)` where *lifetime* is the probe lifetime in seconds and *pulse_len* is the duration of beam on in seconds. After which, the initialized object behaves like a normal function and can be used as such. 

Pulsed functions require double exponential intergration provided in the "FastNumericalIntegration_src" directory. This directory also contains the `integration_fns.cpp` and corresponding header file where the fitting functions are defined. These are then externed to the cython module `integrator.pyx`. 
