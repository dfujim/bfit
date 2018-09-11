# bfit
Beta-NMR GUI for reading, drawing, fitting data. 

## Run Instructions

Call `python3 -m bfit` from the containing directory (the one above bfit/). 

## Setup after Install

Install is done simply by `pip install bfit`. Afterwards, you may want to tell bfit where the data is stored. This is done by defining environment variables
`BNMR_ARCHIVE` and `BNQR_ARCHIVE` (for convenience add this to your .bashrc script). The expected file format is as follows: 

    /path/
        bnmr/
        bnqr/
            2017/
            2018/
                045123.msr

In this example, you would set `BNQR_ARCHIVE=/path/bnqr/` to the directory containing the year directories.
    
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
