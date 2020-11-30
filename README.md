# bfit

A Python application for the analysis of β-NMR and β-NQR data taken at TRIUMF. 

## Run Instructions

To run the graphical user interface, call `bfit` in a terminal. 

bfit also provides the following classes and functions at the top level:

### Functions
* [`bfit.pulsed_exp`](Pulsed-Exponential-Function)
* [`bfit.pulsed_biexp`](Pulsed-Bi-Exponential-Function)
* [`bfit.pulsed_strexp`](Pulsed-Streched-Exponential-Function)
* [`bfit.lorentzian`](Lorentzian-Function)
* [`bfit.bilorentzian`](Bi-Lorentzian-Function)
* [`bfit.quadlorentzian`](Quad-Lorentzian-Function)
* [`bfit.gaussian`](Gaussian-Function)
    
### Curve Fitting
* [`bfit.minuit`](Minuit)
* [`bfit.global_fitter`](Global-Fitter)
* [`bfit.global_bdata_fitter`](Global-Fitter-for-β-NMR)
* [`bfit.fit_bdata`](Fit-bdata)

A full description of the API is [here](https://github.com/dfujim/bfit/wiki/API-Reference). 


## Setup

### Dependencies needed pre-install

* Cython: `pip3 install --user Cython`
* numpy: `pip3 install --user numpy`
* Tkinter for python3: `sudo apt-get install python3-tk` (for example), 
* python version 3.6 or higher

### Install instructions

`pip3 install --user bfit`

### Optional seteup

You may want to tell bfit where the data is stored. This is done by defining environment variables
`BNMR_ARCHIVE` and `BNQR_ARCHIVE` (for convenience add this to your .bashrc script). The expected file format is as follows: 

    /path/
        bnmr/
        bnqr/
            2017/
            2018/
                045123.msr

In this example, you would set `BNQR_ARCHIVE=/path/bnqr/` to the directory containing the year directories.

If bfit cannot find the data, it will attempt to download the files from [musr.ca](http://musr.ca/mud/runSel.html) according to the defaults set in the [bdata](https://pypi.org/project/bdata/) package. 
