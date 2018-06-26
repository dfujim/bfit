# bfit
Beta-NMR GUI for reading, drawing, fitting data. 

## Dependencies and Compiling

1. Clone the `bdata` repository and ensure this is on your `PYTHONPATH`. This has the bdata object and mudpy module which one needs to fetch bnmr data. 
2. Compile the cython modules in `./Fitting/`. One can also use these to build their own fitting modules. 

## Run Instructions

Call `./bfit.py` or `python3 bfit.py`, or set up an alias to do so. 

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