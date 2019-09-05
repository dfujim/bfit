# bfit
Beta-NMR GUI for reading, drawing, fitting data. 

## Run Instructions

To run, call `python3 -m bfit`

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

If bfit cannot find the data, it will attempt to download the files from [musr.ca](http://musr.ca/mud/runSel.html) according to the defaults set in the [bdata](https://pypi.org/project/bdata/) package. 

## Operation Details

See [here](https://github.com/dfujim/bfit/blob/master/bfit/fitting/README.md) for the bfit fitting submodule documentation. 
