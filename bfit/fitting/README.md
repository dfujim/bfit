# API Reference

## Summary

### Fit Functions

| Function / Constructor | Description |
| :-- | :-- |
| [`lorentzian(freq, peak, fwhm, amp)`](#Lorentzian-Function) | Lorentzian function with height set by `amp` |
| [`bilorentzian(freq, peak, fwhmA, ampA, fwhmB, ampB)`](#Bi-Lorentzian-Function) | Superposition of two Lorentzian functions, with equal peak location |
| [`quadlorentzian(freq, nu_0, nu_q, eta, theta, phi, amp0, amp1, amp2, amp3, fwhm0, fwhm1, fwhm2, fwhm3, I)`](#Quad-Lorentzian-Function) | Superposition of four Lorentzians according to quadrupole splitting 2nd order perturbation theory |
| [`gaussian(freq, mean, sigma, amp)`](#Gaussian-Function) | Gaussian function with height set by `amp` |
| [`pulsed_exp`](#Pulsed-Exponential-Function) | Exponential convoluted with square beam pulse |
| [`pulsed_biexp`](#Pulsed-Bi-Exponential-Function) | Supeposition of two pulsed exponentials |
| [`pulsed_strexp`](#Pulsed-Stretched-Exponential-Function) | Stretched exponential convoluted with square beam pulse |
      
### Curve Fitting 

| Funciton / Constructor | Description |
| :-- | :-- |
|[`global_fitter(fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, shared=None, fixed=None, metadata=None, fprime_dx=1e-6)`](#Global-Fitter) | Chi-squared minimization with parameters shared across multiple data sets |
|[`global_bdata_fitter(data, fn, xlims=None, rebin=1, asym_mode='c', **kwargs)`](#Global-Fitter-for-β-NMR) | Same as `global_fitter` but with β-NMR specific input |
|[`fit_bdata(data, fn, omit=None, rebin=None, shared=None, hist_select='', xlims=None, asym_mode='c', fixed=None, minimizer='migrad+minos', **kwargs)`](#Fit-bdata) | β-NMR fitting backend for GUI |
|[`minuit(fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, fn_prime=None, fn_prime_dx=1e-6, name=None, start=None, error=None, limit=None, fix=None, print_level=1, **kwargs)`](#Minuit) | iminuit wrapper with pre-defined least squares equations for ease of use |

## Lorentzian Function
## Bi-Lorentzian Function
## Quad-Lorentzian Function
## Gaussian Function
## Pulsed Exponential Function
## Pulsed Bi-Exponential Function
## Pulsed Stretched Exponential Function
## Global Fitter
## Global Fitter for β-NMR
## Fit bdata
## Minuit
