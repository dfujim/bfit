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
| [`pulsed_biexp`](#Pulsed-Bi-Exponential-Function) | Superposition of two pulsed exponentials |
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
* `fracb`: Fraction of the output attributed to the component with 1/T<sub>1</sub><sup>(b)</sup>. Valid only in the range [0, 1]
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

Stretched exponential convoluted with square beam pulse for fitting pulsed β-NMR spin-lattice relaxation (SLR) measurements. 

**Constructor**

```python
class pulsed_strexp(lifetime, pulse_len)
```

* `lifetime`: Nuclear lifetime of the probe. See also [lifetimes defined in bdata](https://github.com/dfujim/bdata#life)
* `pulse_len`: Duration of the beam on pulse in seconds. See also the `get_pulse_s` function from [bdata](https://github.com/dfujim/bdata#bdata)

**Call**
```python
def pulsed_strexp(time, lambda_s, beta, amp)
```

* `time`: Times at which to evaluate the function. Must be an `np.ndarray` > 0.
* `lambda_s`: SLR rate, equivalent to 1/T<sub>1</sub>
* `beta`: stretchin exponent
* `amp`: Initial asymmetry

**Returns**

Stretched exponential function convoluted with beam pulse, with the same shape as `time`. 

Unlike the [pulsed exponential](#Pulsed-Exponential-Function), no closed form solution exists for the stretched exponential. The equivalent integrals are computed numerically with a [double-exponential intergration scheme](https://www.codeproject.com/Articles/31550/Fast-Numerical-Integration):

During the beam pulse: 

<img src="https://render.githubusercontent.com/render/math?math=\Large \mathcal{P}(t) = \frac{p_0}{\tau[1-\exp(-t/\tau)]} \int_0^t \exp\left[\frac{-(t-t')}{\tau}\right]p(t-t')dt'">

and after the pulse:

<img src="https://render.githubusercontent.com/render/math?math=\Large \mathcal{P}(t) = \frac{p_0}{\tau\exp(-t/\tau)[\exp(-\Delta/\tau)-1]} \int_0^\Delta \exp\left[\frac{-(t-t')}{\tau}\right]p(t-t')dt'">


where 

* <img src="https://render.githubusercontent.com/render/math?math=p_0"> is the initial polarization at the moment of implantation,
* <img src="https://render.githubusercontent.com/render/math?math=\tau"> is the nuclear lifetime of the probe, 
* <img src="https://render.githubusercontent.com/render/math?math=t'"> is time of implantation,
* <img src="https://render.githubusercontent.com/render/math?math=p(t-t') = \exp\left[-\left(\frac{t-t'}{T_1}\right)^\beta\right]"> is the stretched exponential function, 
* <img src="https://render.githubusercontent.com/render/math?math=T_1"> is the SLR relaxation time,
* <img src="https://render.githubusercontent.com/render/math?math=\Delta"> is the duration of the beam on time.

**Example**
```python
import bfit
import matplotlib.pyplot as plt
pexp = bfit.pulsed_strexp(1.21, 4)    # 8Li probe with 4s beam pulse
t = np.linspace(0, 10, 500) + 1e-9    # required t > 0
plt.plot(t, pexp(t, 0.5, 0.5, 1))
```

## Global Fitter

Chi-squared minimization with parameters shared across multiple data sets.

**Constructor**

```python
class global_fitter(fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, shared=None, fixed=None, metadata=None, fprime_dx=1e-6)
```

* `fn`: Function handle, or list of function handles. Fit this to the data `x` and `y`
* `x`: Independent variable
* `y`: Dependent variable
* `dy`: [optional] Error in `y`
* `dx`: [optional] Error in `x`
* `dy_low`: [optional] Used when `y` has asymmetric errors. In this case `dy` is the upper error
* `dx_low`: [optional] Used when `x` has asymmetric errors. In this case `dx` is the upper error
* `shared`: **[mandatory]** Boolean list specifiying which parameters of `fn` are shared globally
* `fixed`: [optional] Boolean list specifiying which parameters of `fn` are fixed to their initial parameters
* `metadata`: [optional] List of fixed values to pass to function. `len(metadata)` must equal the number of data sets
* `fprime_dx`: `x` spacing for calculating centered differences derivative in `fn`

Data inputs and their errors must be organized as such: 

```python
x = [[a, b, c, ...],    # data set 1
     [d, e, f, ...],    # data set 2
     ...
     ]
```

Each data set is not requred to be of the same length. 

**Attributes**

| Attribute | Description |
| :-- | :-- |
| `chi` | list of chisquared values for each data set |
| `chi_glbl` | global chisqured |
| `cov` | fit covarince matrix with unnecessary variables stripped |
| `cov_runwise` | fit covarince matrix run-by-run with all needed inputs |
| `fn` | list of fitting function handles |
| `fixed` | list of fixed variables (corresponds to input) |
| `fprime_dx` | x spacing in calculating centered differences derivative |
| `metadata` | array of additional inputs, fixed for each data set (`if len(shared) < len(actual inputs)`) |
| `minuit` | `iminuit.Minuit` object for minimizing with migrad algorithm |
| `minimizer` | One of `trf`, `dogbox`, `migrad`, or `minos` |
| `npar` | number of parameters in input function |
| `nsets` | number of data sets |
| `par` | fit results with unnecessary variables stripped |
| `par_runwise` | fit results run-by-run with all needed inputs |
| `shared` | array of bool of `len = npar`, share parameter if true |
| `sharing_links` | 2D array of ints, linking global inputs to function-wise inputs |
| `std_l`, `std_u` | lower/upper errors with unnecessary variables stripped |
| `std_l_runwise`, `std_u_runwise` | lower/upper errors run-by-run with all needed inputs |
| `x` | input array of x data sets [array1, array2, ...] |
| `xcat` | concatenated x data for global fitting |
| `y` | input array of y data sets [array1, array2, ...] |
| `ycat` | concatenated y data for global fitting |
| `dx` | input array of x error data sets [array1, array2, ...] |
| `dxcat` | concatenated x error data for global fitting |
| `dy` | input array of x error data sets [array1, array2, ...] |
| `dycat` | concatenated x error data for global fitting |
| `dx_low` | input array of x lower error data sets [array1, array2, ...] |
| `dxcat_low` | concatenated x lower error data for global fitting |
| `dy_low` | input array of y lower error data sets [array1, array2, ...] |
| `dycat_low` | concatenated y lower error data for global fitting |

**Draw Function**

```python
def draw(mode='stack', xlabel='', ylabel='', do_legend=False, labels=None, savefig='', **errorbar_args)
```

Draw the fit

* `mode`: one of `stack`, `new`, `append` (or first character for shorhand)
* `xlabel`: string, label for the x axis
* `do_legend`: boolean, if True, draw with legend
* `labels`: list of strings identifying each data set in the legend
* `savefig`: if not `''`, save the figure as this string
* `errorbar_args`: keyword arguments to pass to `matplotlib.pyplot.errorbar`

Returns list of `matplotlib.pyplot.figure` objects with drawn fits and data

**Fit Function**

```python
def fit(minimizer='migrad', **fitargs)
```

Run the fit

* `minimizer`: One of `trf`, `dogbox`, `migrad`, or `minos` indicating which algorithm to use in minimizing chi-squared. Both `trf` and `dogbox` are implemented in [`scipy.optimize.curve_fit`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html). Both `migrad` and `minos` are implemented in the [`iminuit`](https://iminuit.readthedocs.io/en/stable/) package and call the MIGRAD algorithm, although the `minos` option will additionally call the MINOS error solving algorithm. 

Keyword arguments

* `p0`: initial parameters. May take two different shapes:
     * `[(p1, p2, ...), ...]`: innermost tuple is initial parameters for each data set, list of tuples for all data sets (`p0.shape = (nsets, npars)`).
     * `(p1, p2, ...)`: single tuple to set same initial parameters for all data sets, broadcasted internally to match the prior option (`p0.shape = (npars, )`).
* `bounds`: fitting limits. May take two different shapes:
     * `[((lower1, lower2, ...), (upper1, upper2, ...)), ...]`: similar to `p0` option 1, but use 2-tuples instead of 1-tuples (`bounds.shape = (nsets, 2, npars)`).
     * `((lower1, lower2, ...), (upper1, upper2, ...))`: single 2-tuple to set same bounds for all data sets (`bounds.shape = (2, npars)`).

Returns tuple of output arrays: `(parameters, lower errors, upper errors, covariance matrix)` with the same format as `get_par()` (below)

**Get Chi-Squared Function**

```python
def get_chi()
```

Calculate the chi-squared per degree of freedom for each data set, and globally. 

Returns `(global chi2, list of chi2)`

The chi-squared calculation follows the procedure outlined in the [`minuit`](#Minuit) object, noting that both the `trf` and `dogbox` algorithms use an internal chi-squared calculation and do not account for asymmetric errors or errors in x. 

**Get Parameters and Errors Function**

```python
def get_par()
```

Get the parameters of best fit, organized data-set-wise. 

Return 4-tuple of `(parameters, lower errors, upper errors, covariance matrix)` with format

```python
( [ [par1_data1, par2_data1, ...],
    [par1_data2, par2_data2, ...], 
    ...],
  [ [low1_data1, low2_data1, ...], 
    [low1_data2, low2_data2, ...], 
    ...],
  [ [upp1_data1, upp2_data1, ...],
    [upp1_data2, upp2_data2, ...],
    ...],
  [ [cov1_data1, cov2_data1, ...], 
    [cov1_data2, cov2_data2, ...], 
    ...]
)
```

**Example**

```python
import bfit
import numpy as np

x = [np.arange(10), np.arange(11)]
y = [np.arange(10)**2, np.arange(11)**2+4]
f = lambda x, a, b: x**a + b

# fit with shared exponent
gf = bfit.global_fitter(f, x, y, shared=[True, False])
gf.fit(p0 = [2, 1], bounds = [[0, -np.inf], [np.inf, np.inf]])
par, errl, erru, cov = gf.get_par()
gchi, chi = gf.get_chi()
gf.draw('append')

# fit with fixed offset in first function only
gf = bfit.global_fitter(f, x, y, shared=[True, False], fixed = [[False, True], [False, False]])
gf.fit(p0 = [2, 10], bounds = [[0, 0], [np.inf, np.inf]])
gf.draw('append')
```

## Global Fitter for β-NMR

Uses `global_fitter` to fit β-NMR asymmetry, calculated by the [bdata object](https://github.com/dfujim/bdata).

**Constructor**

```python
class global_bdata_fitter(data, fn, xlims=None, rebin=1, asym_mode='c', **kwargs)
```

* `data`: list of bdata objects
* `fn`: Function handle, or list of function handles (same as [`global_fitter`](#Global-Fitter))
* `xlims`: list of 2-tuples for (low, high) bounds on fitting range based on x values. If list is not depth 2, use this range on all runs
* `rebin`: asymmetry rebinning factor for both fitting and drawing
* `asym_mode`: asymmetry type to calculate and fit
* `kwargs`: keyword arguments to pass to [`global_fitter`](#Global-Fitter)


## Fit bdata

Function for fitting a list of bdata objects with shared or independant variables. Backend to GUI fitting. 

```python
def fit_bdata(data, fn, omit=None, rebin=None, shared=None, hist_select='', xlims=None, asym_mode='c', fixed=None, minimizer='migrad', **kwargs)
```

* `data`: list of [bdata objects](https://github.com/dfujim/bdata) (or single object)
* `fn`: Function handle, or list of function handles (same as [`global_fitter`](#Global-Fitter))
* `omit`: list of strings of space-separated bin ranges to omit
* `rebin`: asymmetry rebinning factor for both fitting and drawing
* `shared`: Boolean list specifiying which parameters of `fn` are shared globally
* `xlims`: list of 2-tuples for (low, high) bounds on fitting range based on x values. If list is not depth 2, use this range on all runs
* `asym_mode`: asymmetry type to calculate and fit, passed to [bdata](https://github.com/dfujim/bdata)
* `fixed`: Boolean list specifiying which parameters of `fn` are fixed to their initial parameters
* `minimizer`: One of `trf`, `dogbox`, `migrad`, or `minos` indicating which algorithm to use in minimizing chi-squared. Both `trf` and `dogbox` are implemented in [`scipy.optimize.curve_fit`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html). Both `migrad` and `minos` are implemented in the [`iminuit`](https://iminuit.readthedocs.io/en/stable/) package and call the MIGRAD algorithm, although the `minos` option will additionally call the MINOS error solving algorithm. 
* `kwargs`: keyword arguments for [curve_fit](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html)/[minuit](https://iminuit.readthedocs.io/en/stable/).

**Returns**

Tuple of `(par, std_l, std_h, cov, chi, gchi)`, where
            
* `par`:    array of best fit parameters
* `std_l`:  array of lower best fit errors
* `std_h`:  array of upper best fit errors
* `cov`:    2D array, covariance matrix
* `chi`:    array of chisquare of each fit
* `gchi`:   global chisquared of fits

## Minuit

Conveience wrapper for the [`iminuit.Minuit`](https://iminuit.readthedocs.io/en/stable/) class, with pre-defined chi-squared.

**Constructor**

```python
minuit(fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, fn_prime=None, fn_prime_dx=1e-6, name=None, start=None, error=None, limit=None, fix=None, print_level=1, **kwargs)
```

* `fn`: function handle. f(x, a, b, c, ...)
* `x`: x data
* `y`: y data
* `dy`: [optional] error in y
* `dx`: [optional] error in x
* `dy_low`: [optional] if error in y is asymmetric. If not none, dy is upper error
* `dx_low`: [optional] if error in y is asymmetric. If not none, dx is upper error
* `fn_prime`: [optional] function handle for the first derivative of `fn`. f'(x, a, b, c, ...)
* `fn_prime_dx`: Spacing in x to calculate the derivative for default calculation
* `name`: [optional] sequence of strings. If set, use this for 
* `start`: [optional] sequence of numbers. Required if the function takes an array as input or if it has the form `f(x, *pars)`, and name is not defined. Default: 1, broadcasted to all inputs
* `error`: [optional] sequence of numbers. Initial step sizes. 
* `limit`: [optional] sequence of limits that restrict the range format: `[[low, high], [low, high], ...]` in which a parameter is varied by minuit., with `None`, `inf` or `-inf` used to disable limit
* `fix`: [optional] sequence of booleans. Default: `False`
* `print_level`: Set the print_level
    * 0 is quiet. 
    * 1 prints out at the end of MIGRAD/HESSE/MINOS. 
    * 2 prints debug messages.
* `kwargs`: passed to `Minuit.from_array_func` and `Minuit`. To set for parameter "a" one can assign the following keywords instead of the array inputs:
    * `a` = initial_value
    * `error_a` = start_error
    * `limit_a` = (low, high)
    * `fix_a` = True
    
The chi-squared is caluclated to include both errors in x and asymmetric errors, following the procedure outlined by [ROOT](https://root.cern.ch/doc/master/classTGraph.html#aa978c8ee0162e661eae795f6f3a35589):

<img src="https://render.githubusercontent.com/render/math?math=\Large \chi^2 = \sum\frac{[y-f(x)]^2}{\sigma_y^2 %2B [\frac{1}{2}(\sigma_{xlow} %2B \sigma_{xup})f'(x)]^2}"> 

where 

* <img src="https://render.githubusercontent.com/render/math?math=\sigma_y"> is the error in _y_, where <img src="https://render.githubusercontent.com/render/math?math=\sigma_y = \sigma_{ylow}"> if <img src="https://render.githubusercontent.com/render/math?math=f(x) < y"> and <img src="https://render.githubusercontent.com/render/math?math=\sigma_y = \sigma_{yup}"> if <img src="https://render.githubusercontent.com/render/math?math=f(x) > y">
* <img src="https://render.githubusercontent.com/render/math?math=\sigma_{xlow}"> is the lower error in x
* <img src="https://render.githubusercontent.com/render/math?math=\sigma_{xup}"> is the upper error in x
