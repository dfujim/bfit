# bfit
Beta-NMR GUI for reading, drawing, fitting data. 

## Run Instructions

To run the gui, call `bfit`

bfit also provides the following classes and functions at the top level:

* Functions
    * `bfit.pulsed_exp`
    * `bfit.pulsed_strexp`
    * `bfit.pulsed_biexp`
    * `bfit.lorentzian` 
    * `bfit.bilorentzian`
    * `bfit.quadlorentzian`
    * `bfit.gaussian`
    
* Minimization
    * `bfit.minuit`
    * `bfit.global_fitter`
    * `bfit.global_bdata_fitter`
    * `bfit.fit_bdata`

A description of these functions can be found [here](https://github.com/dfujim/bfit/blob/master/bfit/fitting/README.md). 


## Setup

### Dependencies needed pre-install

* Cython: `pip3 install Cython`
* numpy: `pip3 install numpy`
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
