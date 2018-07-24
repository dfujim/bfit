# bfit
Beta-NMR GUI for reading, drawing, fitting data. 

## Dependencies and Compiling

1. bdata: can be installed with `pip install bdata` 
2. Compile the cython integrator in `bfit/fitting/`. One can also use this to build their own fitting modules. This is done with  `python3 setup_integrator.py build_ext --inplace` from within the fitting directory. 

## Run Instructions

Call `python3 -m bfit` from the containing directory (the one above bfit/). 

## A Tour of the GUI

### Menu bar: 

* **File**
    * Calculators for B0 in BNQR and B1 in BNMR
    * Export fetche data to csv file
* **Settings**
    * Set matplotlib defaults: drawing styles
    * Set data directory. Defaults to environment variables `BNMR_ARCHIVE` and `BNQR_ARCHIVE`
* **Redraw Mode**
    * Set drawing mode. See help for details on hotkeys. 
* **Help**
    * Show help wiki.

### Tabs:

* **File Details**
    * File inspector. Use this to quickly view the contents and parameters of a given run. Use `return` to fetch and `ctrl+return` to quickly draw. 
* **Fetch Data**
    * Fetch many data files for quick superposition and to set up fitting routines. Data fetched here will be fitted on the next tab. See help for hotkey details. 
* **Fit Data**
    * Fit the fetched data, and set fitting parameters. 
* **View Fit Results**
    * View the fit parameters and draw as functions of each other. 