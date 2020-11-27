# API Reference

## Summary

### Fit Functions

| Function / Constructor | Description |
| :-- | :-- |
| [`lorentzian(freq, peak, fwhm, amp)`](#Lorentzian-Function) | Lorentzian function with height set by `amp` |
| [`bilorentzian(freq, peak, fwhmA, ampA, fwhmB, ampB)`](#Bi-Lorentzian-Function) | Superposition of two Lorentzian functions, with equal peak location |
| [`quadlorentzian(freq, nu_0, nu_q, eta, theta, phi, amp0, amp1, amp2, amp3, fwhm0, fwhm1, fwhm2, fwhm3, I)`](#Quad-Lorentzian-Function) | Superposition of four Lorentzians according to 2nd order perturbation theory quadrupole splitting |
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
An inverted Lorentzian function (positive amplitude results in negative output) for fitting β-NMR resonances.

**Arguments**
* `freq`: Frequencies at which to evaluate the Lorentzian. Can be a `float` or an `np.ndarray`
* `peak`: Location of the peak
* `fwhm`: Full width at the half-maximum
* `amp`: Height of the function (minimum value, given that the function is inverted)

**Returns**

Lorentzian equation with the same shape as `freq`, according to the equation

<img src="https://render.githubusercontent.com/render/math?math=\Large L(x, x_0, \Gamma, A) = -A\frac{\left(\frac{1}{2}\Gamma\right)^2}{(x-x_0)^2%2B\left(\frac{1}{2}\Gamma\right)^2}">

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

Superimposed Lorentzian equations with the same shape as `freq`. Equivalent to `lorentzian(freq, peak, fwhmA, ampA) + lorentzian(freq, peak, fwhmB, ampB)`.

**Example**
```python
bilorentzian(np.arange(100), 50, 10, 1, 0.1, 0.5)
```

## Quad-Lorentzian Function

```python
def quadlorentzian(freq, nu_0, nu_q, eta, theta, phi, 
                   amp0, amp1, amp2, amp3, 
                   fwhm0, fwhm1, fwhm2, fwhm3, I)
```

Superposition of Lorentzians according to 2nd order perturbation theory quadrupole splitting of the Zeeman interaction.

**Arguments**
* `freq`: Frequencies at which to evaluate the function. Can be a `float` or an `np.ndarray`
* `nu_0`: Larmor frequency 
* `nu_q`: Quadrupole splitting frequency 
* `eta`: Electric field gradient asymmetry in the range [0, 1]
* `theta`: Azimuthal angle of the principal axis system (β in notation of Euler angles in the paper)
* `phi`: Polar angle of the principal axis system (α in notation of Euler angles in the paper)
* `amp#`: Amplitudes of each of the peaks
* `fwhm#`: Full width at half maximum of each of the peaks
* `I`: Total nuclear spin

The definition of the quadrupole splitting frequency in this formulation is:

<img src="https://render.githubusercontent.com/render/math?math=\Large \nu_q = \frac{3e^2Qq}{4I(2I-1)}">

**Returns**

Superimposed Lorentzian equations whose peak values correspond to the locations of a split Zeeman interaction by a quadrupole interaction with an electric field gradient. 

Reference: [P. P. Man, "Quadrupolar Interactions", in Encyclopedia of Magnetic Resonance, edited by R. K. Harris and R. E. Wasylishen](https://doi.org/10.1002/9780470034590.emrstm0429.pub2)
        
**Example**
```python
quadlorentzian(np.linspace(1e6,1e6+200,1000), 1e6+100, 10, 1, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2)
```

## Gaussian Function

```python
def gaussian(freq, mean, sigma, amp)
```

Your standard Gaussian function, inverted for ease of fitting β-NMR resonances.

**Arguments**
* `freq`: Frequencies at which to evaluate the function. Can be a `float` or an `np.ndarray`
* `mean`: Location of the peak, coincident with the average
* `sigma`: Standard deviation of the distribution
* `amp`: Height of the function (minimum value, given that the function is inverted)

**Returns**

Gaussian function according to 

<img src="https://render.githubusercontent.com/render/math?math=\Large G(x, \mu, \sigma, A) = -A \cdot \exp\left(-\frac{1}{2}\frac{(x-\mu)^2}{\sigma^2}\right)">

See also [wolfram alpha](https://mathworld.wolfram.com/GaussianFunction.html) for details.

**Example**
```python
gaussian(np.arange(100), 50, 10, 1)
```

## Pulsed Exponential Function

Exponential convoluted with square beam pulse for fitting pulsed β-NMR spin-lattice relaxation (SLR) measurements. 

**Constructor**

```python
class pulsed_exp(lifetime, pulse_len)
```

* `lifetime`: Nuclear lifetime of the probe. See also [lifetimes defined in bdata](https://github.com/dfujim/bdata#life)
* `pulse_len`: Duration of the beam on pulse in seconds. See also the `get_pulse_s` function from [bdata](https://github.com/dfujim/bdata#bdata)

**Call**
```python
def pulsed_exp(time, lambda_s, amp)
```

* `time`: Times at which to evaluate the function. Must be an `np.ndarray`.
* `lambda_s`: SLR rate, equivalent to 1/T<sub>1</sub>
* `amp`: Initial asymmetry

**Returns**

Exponential function convoluted with beam pulse, with the same shape as `time`. 

During the pulse, the output is given by: 

<img src="https://render.githubusercontent.com/render/math?math=\Large \mathcal{P}(t) = p_0 \left(\frac{\tau'}{\tau}\right) \left(\frac{1-\exp(-t/\tau')}{1-\exp(-t/\tau)}\right)">

and after the pulse the output is 

<img src="https://render.githubusercontent.com/render/math?math=\Large \mathcal{P}(t) = p_0 \left(\frac{\tau'}{\tau}\right) \left(\frac{\exp(-t/T_1)[1-\exp(-\Delta/\tau')]}{1-\exp(-\Delta/\tau)}\right)">

where 

* <img src="https://render.githubusercontent.com/render/math?math=p_0"> is the initial polarization at the moment of implantation,
* <img src="https://render.githubusercontent.com/render/math?math=\tau"> is the nuclear lifetime of the probe, 
* <img src="https://render.githubusercontent.com/render/math?math=T_1"> is the SLR relaxation time,
* <img src="https://render.githubusercontent.com/render/math?math=1/\tau' = 1/\tau %2B 1/T_1">,
* <img src="https://render.githubusercontent.com/render/math?math=\Delta"> is the duration of the beam on time.

The above two equations together form the peicewise definition of the pulsed exponential function. 

**Example**
```python
import bfit
import matplotlib.pyplot as plt
pexp = bfit.pulsed_exp(1.21, 4)    # 8Li probe with 4s beam pulse
t = np.linspace(0, 10, 500)
plt.plot(t, pexp(t, 0.5, 1))
```

## Pulsed Bi-Exponential Function

Superposition of two pulsed exponentials, for convenience. 

**Constructor**

```python
class pulsed_biexp(lifetime, pulse_len)
```

* `lifetime`: Nuclear lifetime of the probe. See also [lifetimes defined in bdata](https://github.com/dfujim/bdata#life)
* `pulse_len`: Duration of the beam on pulse in seconds. See also the `get_pulse_s` function from [bdata](https://github.com/dfujim/bdata#bdata)

**Call**
```python
def pulsed_biexp(time, lambda_s, lambdab_s, fracb, amp)
```

* `time`: Times at which to evaluate the function. Must be an `np.ndarray`.
* `lambda_s`: SLR rate, equivalent to 1/T<sub>1</sub>
* `lambdab_s`: SLR rate of the other component, equivalent to 1/T<sub>1</sub><sup>(b)</sup>
* `fracb`: Fraction of the output attributed to the component with 1/T<sub>1</sub><sup>(b)</sup> 
* `amp`: Initial asymmetry

**Returns**

Bi-exponential function convoluted with beam pulse, with the same shape as `time`. Equivalent to `(1-fracb)*pulsed_exp(time, lambda_s, amp) + fracb*pulsed_exp(time, lambdab_s, amp)`

**Example**
```python
import bfit
import matplotlib.pyplot as plt
pexp = bfit.pulsed_biexp(1.21, 4)    # 8Li probe with 4s beam pulse
t = np.linspace(0, 10, 500)
plt.plot(t, pexp(t, 0.5, 1, 0.5, 1))
```

## Pulsed Stretched Exponential Function
## Global Fitter
## Global Fitter for β-NMR
## Fit bdata
## Minuit
