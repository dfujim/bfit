# Module Map

Submodules and function signatures: 

* **`bfit.fitting.functions`** (base functions module)
    * [`lorentzian(freq,peak,width,amp)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L24-L25)
    * [`bilorentzian(freq,peak,widthA,ampA,widthB,ampB)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L27-L29)
    * [`gaussian(freq,mean,sigma,amp)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L31-L32)
    * `pulsed_exp`
        * constructor: [`pulsed_exp(lifetime,pulse_len)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L40-L45)
        * call: [`pulsed_exp(time,lambda_s,amp)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L56-L57)
    * `pulsed_biexp`
        * constructor: [`pulsed_biexp(lifetime,pulse_len)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L40-L45)
        * call: [`pulsed_biexp(time,lambda_s,lambdab_s,fracb,amp)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L60-L62)
    * `pulsed_strexp`
        * constructor: [`pulsed_strexp(lifetime,pulse_len)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L40-L45)
        * call: [`pulsed_strexp(time,lambda_s,beta,amp)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L65-L66)
    * [`get_fn_superpos(fn_handles)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/functions.py#L71-L79)
* **`bfit.fitting.fit_bdata`** (fitting bdata files module)
    * [`fit_list(runs,years,fnlist,omit=None,rebin=None,sharelist=None,npar=-1,hist_select='',**kwargs)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/fit_bdata.py#L13-L60)
    * [`fit_single(run,year,fn,omit='',rebin=1,hist_select='',**kwargs)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/fit_bdata.py#L171-L207)
* [**`bfit.fitting.global_fitter`**](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/global_fitter.py#L50-L80) (general global fitting)
    * constructor: [`global_fitter(x,y,dy,fn,sharelist,npar=-1)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/global_fitter.py#L88-L105)
    * [`draw(mode='stack',xlabel='',ylabel='',do_legend=False,labels=None,savefig='',**errorbar_args)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/global_fitter.py#L140-L160)
    * [`fit(**fitargs)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/global_fitter.py#L222-L251)
    * [`get_chi()`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/global_fitter.py#L311-L318)
    * [`get_par()`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/global_fitter.py#L341-L350)
* [**`bfit.fitting.global_bdata_fitter`**](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/global_bdata_fitter.py#L11-L12) (global fitting of bdata objects, inherits from `global_fitter`)
    * constructor: [`global_bdata_fitter(runs,years,fn,sharelist,npar=-1)`](https://github.com/dfujim/bfit/blob/d8feb0e12d3aae682917a9ac47d3d19f32eb8885/bfit/fitting/global_bdata_fitter.py#L14-L40)
* **`bfit.fitting.decay_31mg`** (fractional activity of 31Mg probe and decay products)
   * `fn_31Mg(time,beam_pulse,beam_rate=1e6)` (fractions of total atoms. Similar for 31Al, 31Si, 31P, 30Al, 30Si.)
   * `fa_31Mg(time,beam_pulse,beam_rate=1e6)` (fractional activity. Similar for 31Al, 31Si, 31P, 30Al, 30Si.)
   

# Module Details

## `bfit.fitting.functions`

The lorentzian and gaussian are standard python functions. The pulsed functions are actually objects. For optimization purposes, they should be first initialized in the following manner: `fn = pulsed_exp(lifetime,pulse_len)` where *lifetime* is the probe lifetime in seconds and *pulse_len* is the duration of beam on in seconds. After which, the initialized object behaves like a normal function and can be used as such. 

Pulsed functions require double exponential intergration provided in the "FastNumericalIntegration_src" directory. This directory also contains the `integration_fns.cpp` and corresponding header file where the fitting functions are defined. These are then externed to the cython module `integrator.pyx`. 

`get_fn_superpos(fn_handles)` takes a list of function handles and returns another function handle whose output is the sum of the input functions. Parameters are mapped appropriately (concatentated in order). 

## `bfit.fitting.fit_bdata`

These are easy fit [bdata object](https://ms-code.phas.ubc.ca:2633/dfujim_public/bdata) functions. The first, `fit_list`, fits a list of functions, possibly with global parameters. A list of fit functions needs to be passed such that different fit functions can be applied to different runs. These fit functions should all have the same signature. 

The second, `fit_single`, fits only a single run. 

## `bfit.fitting.global_fitter`

Global fitting object. 

```text
    Uses scipy.optimize.curve_fit to fit a function or list of functions to a set of data with shared parameters.
    
    Usage: 
        
        Construct fitter:    
            g = global_fitter(x,y,dy,fn,sharelist,npar=-1)        
    
        Fit
            g.fit(**fitargs)
           
        Get chi squared
            g.get_chi()
        
        Get fit parameters
            g.get_par()
            
        Draw the result
            g.draw(mode='stack',xlabel='',ylabel='',do_legend=False,labels=None,
                   savefig='',**errorbar_args)
```        

## `bfit.fitting.global_bdata_fitter`

Inherits from `global_fitter`, but changes the constructor to extract [bdata](https://ms-code.phas.ubc.ca:2633/dfujim_public/bdata) asymmetries. 

## `bfit.fitting.decay_31mg`

Functions to calculate the fraction activity and populations of 31Mg and decay products. To fit 31Mg data, multiply pulsed fitting function with the fractional activity. For example: 

```python 
from bfit.fitting.decay31mg import fa_31Mg
from bfit.fitting.functions import pulsed_exp 
from bdata import life

pexp = pulsed_exp(lifetime=life.Mg31,pulse_len=4)
fitfn = lambda time,*par : pexp(time,*par) * fa_31Mg(time,beam_pulse=4,beam_rate=1e6)
```
Note that the fractional activity is independent of the beam_rate to 14 decimal places, as long as it is non-zero. 
