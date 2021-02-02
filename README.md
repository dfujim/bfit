# bfit

<a href="https://pypi.org/project/bfit/" alt="PyPI Version"><img src="https://img.shields.io/pypi/v/bfit?label=PyPI%20Version"/></a>
<img src="https://img.shields.io/pypi/format/bfit?label=PyPI%20Format"/>
<img src="https://img.shields.io/github/languages/code-size/dfujim/bfit"/>
<img src="https://img.shields.io/tokei/lines/github/dfujim/bfit"/>
<img src="https://img.shields.io/pypi/l/bfit"/>

<a href="https://github.com/dfujim/bfit/commits/master" alt="Commits"><img src="https://img.shields.io/github/commits-since/dfujim/bfit/latest/master"/></a>
<a href="https://github.com/dfujim/bfit/commits/master" alt="Commits"><img src="https://img.shields.io/github/last-commit/dfujim/bfit"/></a>

A Python application for the analysis of β-detected nuclear magnetic and quadrupole resonance (β-NMR and β-NQR) data taken at TRIUMF. These techniques are similar to muon spin rotation (μSR), using a radioactive atomic ion in the place of the muon. bfit has been written to satisfy the following needs: 

* Provide the means for quick on-line analyses during beam time. 
* Provide a useful and flexible API for refined analyses in Python3, in conjunction with [bdata](https://github.com/dfujim/bdata). 
* User-friendly for non-programmers. 
* Be easily maintainable and distributable. 

The intended audience is any user of the the β-NMR or β-NQR spectrometers, be they a new student, visiting scientist, or someone from the local group with decades of experience. 

### Useful links

* [Documentation](https://github.com/dfujim/bfit/wiki)
* [API reference](https://github.com/dfujim/bfit/wiki/API-Reference)
* [GUI Tutorial](https://github.com/dfujim/bfit/wiki/GUI-Tutorial)

### Community Guidelines

* Contributing: Please submit a pull request!
* Reporting issues or seeking support: please create an [issue](https://github.com/dfujim/bfit/issues), and I will get an email with your problem. 

---

## Installation

### Dependencies needed pre-install

| Package | Install Instruction |
|:-- | :--|
Cython | `pip3 install --user Cython` |
NumPy | `pip3 install --user numpy` |
| Tkinter for python3 | [Directions](https://tkdocs.com/tutorial/install.html) |
| python version 3.6 or higher | [Directions](https://www.python.org/downloads/) |

### Installation

|  | Command |
|:-- | :--|
Install as user (recommended) | `pip install --user bfit` |
Install as root | `pip install bfit` |

Note that `pip` should point to the python3 version. If the above does not work try `pip3` or `python3 -m pip` instead.

### Optional Setup

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

### First Startup 

To launch the GUI, simply call 

```bash
bfit
```

in the terminal. If this fails, one can also use the 

```bash
python3 -m bfit
```

syntax, where ``python3`` may be replaced with any python3 executable. 

### Testing your installation 

Testing bfit is most easily accomplished by comparing with a number of other independently developed codes:

* [bnmr_1f](https://gitlab.com/rmlm/bnmr_1f): A command line tool written by R.M.L. McFadden to analyze CW resonance (1f) measurements.
* [bnmr_2e](https://gitlab.com/rmlm/bnmr_2e): A command line tool written by R.M.L. McFadden to analyze pulsed resonance (2e) measurements. 
* [bnmrfit](https://gitlab.com/rmlm/bnmrfit) physica scripts: An older command line tool, well tested through well over a decade of use. The fitting is somewhat minimal however. 
* [BNMROffice](https://github.com/hsaadaoui/bnmroffice): A GUI analysis tool similar to bfit, although out of date with regards to new run modes, and no longer maintained. 
* [musrfit](http://lmu.web.psi.ch/musrfit/user/html/index.html#): A popular and extensive analysis tool for muSR experiments for which a library of [β-NMR functions](http://lmu.web.psi.ch/musrfit/user/html/user-libs.html) has been included by Z. Salman. 

These, and a number of un-published works from R.M.L. McFadden and W.A. MacFarlane, were used to test bfit. Most of them rely on the [MINUIT2 minimizer](https://root.cern.ch/doc/master/Minuit2Page.html) provided by [ROOT](https://root.cern/), so the bfit "migrad" minimizer should be used for a best comparison.

The header information can be checked against that provided from the online [archive search](https://musr.ca/mud/runSel.html). For example, see the run headers for [run 40123 from 2020](https://musr.ca/mud/mud_hdrs.php?ray=Run%2040123%20from%20BNMR%20in%202020&cmd=heads&fn=data/BNMR/2020/040123.msr). 

The user is invited to follow the [usage example](https://github.com/dfujim/bfit/wiki/Example-Usage) to confirm their installation is behaving as expected.
