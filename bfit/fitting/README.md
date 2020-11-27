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

```python
def lorentzian(freq, peak, fwhm, amp)
```
An inverted Lorentzian function (positive amplitude results in negative output) for fitting β-NMR resonances

**Arguments**
* `freq`: Frequencies at which to evaluate the Lorentzian. Can be a `float` or an `np.ndarray`
* `peak`: Location of the peak
* `fwhm`: Full width at the half-maximum
* `amp`: Height of the function (minimum value, given that the function is inverted)

**Returns**

Lorentzian equation with the same shape as `freq`, according to the equation

<img src="https://render.githubusercontent.com/render/math?math=L(x, x_0, \Gamma, A) = -A\frac{\left(\frac{1}{2}\Gamma\right)^2}{(x-x_0)^2%2B\left(\frac{1}{2}\Gamma\right)^2}">

See also [wolfram alpha](https://mathworld.wolfram.com/LorentzianFunction.html) for details.

**Example**
```python
lorentzian(np.arange(100), 50, 10, 1)
```

## Bi-Lorentzian Function

```python
def bilorentzian(freq, peak, fwhmA, ampA, fwhmB, ampB)
```
The superposition of two inverted Lorentzian functions (positive amplitude results in negative output) for fitting β-NMR resonances with the same peak value

**Arguments**
* `freq`: Frequencies at which to evaluate the Lorentzian. Can be a `float` or an `np.ndarray`
* `peak`: Location of the peak
* `fwhmA`: Full width at the half-maximum of one of the Lorentzians
* `ampA`: Height of of one of the Lorentzians
* `fwhmB`: Full width at the half-maximum of the other Lorentzian
* `ampB`: Height of the other Lorentzian

**Returns**

Superimposed Lorentzian equations with the same shape as `freq`. Equivalent to `lorentzian(freq, peak, fwhmA, ampA) + lorentzian(freq, peak, fwhmB, ampB)`

**Example**
```python
bilorentzian(np.arange(100), 50, 10, 1, 0.1, 0.5)
```

## Quad-Lorentzian Function
## Gaussian Function
## Pulsed Exponential Function
## Pulsed Bi-Exponential Function
## Pulsed Stretched Exponential Function
## Global Fitter
## Global Fitter for β-NMR
## Fit bdata
## Minuit
