# bfit

<a href="https://pypi.org/project/bfit/" alt="PyPI Version"><img src="https://img.shields.io/pypi/v/bfit?label=PyPI%20Version"/></a>
<img src="https://img.shields.io/pypi/format/bfit?label=PyPI%20Format"/>
<img src="https://img.shields.io/github/languages/code-size/dfujim/bfit"/>
<img src="https://img.shields.io/tokei/lines/github/dfujim/bfit"/>
<img src="https://img.shields.io/pypi/l/bfit"/>

<a href="https://github.com/dfujim/bfit/commits/master" alt="Commits"><img src="https://img.shields.io/github/commits-since/dfujim/bfit/latest/master"/></a>
<a href="https://github.com/dfujim/bfit/commits/master" alt="Commits"><img src="https://img.shields.io/github/last-commit/dfujim/bfit"/></a>

A Python application for the analysis of β-NMR and β-NQR data taken at TRIUMF. 

## Run Instructions

To run the graphical user interface, call `bfit` in a terminal. 

bfit also provides the following classes and functions at the top level:

### Functions
* [`bfit.pulsed_exp`](https://github.com/dfujim/bfit/wiki/Pulsed-Exponential-Function)
* [`bfit.pulsed_biexp`](https://github.com/dfujim/bfit/wiki/Pulsed-Bi-Exponential-Function)
* [`bfit.pulsed_strexp`](https://github.com/dfujim/bfit/wiki/Pulsed-Streched-Exponential-Function)
* [`bfit.lorentzian`](https://github.com/dfujim/bfit/wiki/Lorentzian-Function)
* [`bfit.bilorentzian`](https://github.com/dfujim/bfit/wiki/Bi-Lorentzian-Function)
* [`bfit.quadlorentzian`](https://github.com/dfujim/bfit/wiki/Quad-Lorentzian-Function)
* [`bfit.gaussian`](https://github.com/dfujim/bfit/wiki/Gaussian-Function)
    
### Curve Fitting
* [`bfit.minuit`](https://github.com/dfujim/bfit/wiki/Minuit)
* [`bfit.global_fitter`](https://github.com/dfujim/bfit/wiki/Global-Fitter)
* [`bfit.global_bdata_fitter`](https://github.com/dfujim/bfit/wiki/Global-Fitter-for-β-NMR)
* [`bfit.fit_bdata`](https://github.com/dfujim/bfit/wiki/Fit-bdata)

A full description of the API is [here](https://github.com/dfujim/bfit/wiki/API-Reference). 


## Setup

### Dependencies needed pre-install

* Cython: `pip3 install --user Cython`
* numpy: `pip3 install --user numpy`
* Tkinter for python3: `sudo apt-get install python3-tk` (for example), 
* python version 3.6 or higher

### Install instructions

`pip3 install --user bfit`

### Optional setup

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
