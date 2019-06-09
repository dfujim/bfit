# Module Map

Submodules and function signatures: 

* **`bfit.fitting.functions`** (base functions module)
    * `lorentzian(freq,peak,width,amp)`
    * `gaussian(freq,mean,sigma,amp)`
    * `pulsed_exp`
        * constructor: `pulsed_exp(lifetime,pulse_len)`
        * call:`pulsed_exp(time,lambda_s,amp)`
    * `pulsed_strexp`
        * constructor: `pulsed_strexp(lifetime,pulse_len)`
        * call:`pulsed_strexp(time,lambda_s,beta,amp)`
    * `get_fn_superpos(fn_handles)`
* **`bfit.fitting.fit_bdata`** (fitting bdata files module)
    * `fit_list(runs,years,fnlist,omit=None,rebin=None,sharelist=None,npar=-1,hist_select='',**kwargs)`
    * `fit_single(run,year,fn,omit='',rebin=1,hist_select='',**kwargs)`
* **`bfit.fitting.global_fitter`** (general global fitting)
    * constructor: `global_fitter(x,y,dy,fn,sharelist,npar=-1)`
    * `draw(mode='stack',xlabel='',ylabel='',do_legend=False,labels=None,savefig='',**errorbar_args`
    * `fit(**fitargs)`
    * `get_chi()`
    * `get_par()`
* **`bfit.fitting.global_bdata_fitter`** (global fitting of bdata objects, inherits from `global_fitter`)
    * constructor: `global_bdata_fitter(runs,years,fn,sharelist,npar=-1)`
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

Docstrings: 

```python
def fit_list(runs,years,fnlist,omit=None,rebin=None,sharelist=None,npar=-1,hist_select='',**kwargs):
    """
        Fit combined asymetry from bdata.
    
        runs:           list of run numbers
        
        years:          list of years corresponding to run numbers, or int which applies to all
        
        fnlist:         list of function handles to fit (or single which applies to all)
                        must specify inputs explicitly (do not do def fn(*par)!)
                        must have len(fn) = len(runs) if list
        
        omit:           list of strings of space-separated bin ranges to omit
        rebin:          list of rebinning of data prior to fitting. 
        
        sharelist:      list of bool to indicate which parameters are shared. 
                        True if shared
                        len = number of parameters.
        
        npar:           number of free parameters in each fitting function.
                        Set if number of parameters is not intuitable from 
                            function code.      
        
        hist_select:    string for selecting histograms to use in asym calc
        
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: par,cov
            par: best fit parameters
            std: standard deviation for each parameter
            chi: chisquared values
    """
```


```python

def fit_single(run,year,fn,omit='',rebin=1,hist_select='',**kwargs):
    """
        Fit combined asymetry from bdata.
    
        runs:           run number
        
        years:          year
        
        fn:             function handle to fit
        
        omit:           string of space-separated bin ranges to omit
        rebin:          rebinning of data prior to fitting. 
        
        hist_select:    string for selecting histograms to use in asym calc
        
        kwargs:         keyword arguments for curve_fit. See curve_fit docs. 
        
        Returns: par,cov
            par: best fit parameters
            std: standard deviation for each parameter
            chi: chisquared value
    """
```

## `bfit.fitting.global_fitter`

Global fitting object. 

```text
    Uses scipy.optimize.curve_fit to fit a function or list of functions to a set of data with shared parameters.
    
    Usage: 
        
        Construct fitter:
            
            g = global_fitter(x,y,dy,fn,sharelist,npar=-1)
            
            
            x,y:        2-list of data sets of equal length. 
                        fmt: [[a1,a2,...],[b1,b2,...],...]
            
            dy:         list of errors in y with same format as y
            
            fn:         function handle OR list of function handles. 
                        MUST specify inputs explicitly
                        if list must have that len(fn) = len(x)
            
            sharelist:  tuple of booleans indicating which values to share. 
                        len = number of parameters 
                        
            npar:       number of free parameters in each fitting function.
                        Set if number of parameters is not intuitable from 
                            function code.
        
    
        Fit
            g.fit(**fitargs)
        
            
            fitargs: parameters to pass to fitter (scipy.optimize.curve_fit) 
            
            p0:         [(p1,p2,...),...] innermost tuple is initial parameters 
                            for each data set, list of tuples for all data sets
                            if not enough sets of inputs, last input is copied 
                            for remaining data sets.
                            
                            p0.shape = (nsets,npars)
                    OR
                        (p1,p2,...) single tuple to set same initial parameters 
                            for all data sets
            
                            p0.shape = (npars,)
            
            bounds:     [((l1,l2,...),(h1,h2,...)),...] similar to p0, but use 
                            2-tuples instead of the 1-tuples of p0
                        
                            bounds.shape = (nsets,2,npars)
                        
                    OR
                        ((l1,l2,...),(h1,h2,...)) single 2-tuple to set same 
                            bounds for all data sets
                            
                            bounds.shape = (2,npars)
                            
                            
            returns (parameters,stdev)
        
            
        Get chi squared
            g.get_chi()
            
            
            Calculate chisq/DOF, both globally and for each function.
            
            sets self.chi and self.chi_glbl
            
            return (global chi, list of chi for each fn)
        
        
        Get fit parameters
            g.get_par()
            
            
            Fetch fit parameters as dictionary
            
            return 2-tuple of (par,error) each with format
            
            [data1:[par1,par2,...],data2:[],...]
        
            
        Draw the result
        
            g.draw(mode='stack',xlabel='',ylabel='',do_legend=False,labels=None,
                   savefig='',**errorbar_args)
           
            
            Draw data and fit results. 
            
            mode:           drawing mode. 
                            one of 'stack', 'new', 'append' (or first character 
                                for shorhand)
            
            xlabel/ylabel:  string for axis labels
            
            do_legend:      if true set legend
            
            labels:         list of string to label data
            
            savefig:        if not '', save figure with this name
            
            errorbar_args:  arguments to pass on to plt.errorbar
            
            Returns list of matplotlib figure objects
```        

## `bfit.fitting.global_bdata_fitter`

Inherits from `global_fitter`, but changes the constructor to extract [bdata](https://ms-code.phas.ubc.ca:2633/dfujim_public/bdata) asymmetries. 

Constructor: 

```python
global_bdata_fitter(runs,years,fn,sharelist,npar=-1):
        """
            runs:       list of run numbers
            
            years:      list of years corresponding to run numbers, or int which applies to all
            
            fn:         list of function handles to fit (or single which applies to all)
                        must specify inputs explicitly (do not do def fn(*par)!)
                        must have len(fn) = len(runs) if list
                        
            sharelist:  list of bool to indicate which parameters are shared. 
                        True if shared
                        len = number of parameters.
                        
            npar:       number of free parameters in each fitting function.
                        Set if number of parameters is not intuitable from function code.            
        """
```

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
