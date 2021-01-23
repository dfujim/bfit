# bfit

<a href="https://pypi.org/project/bfit/" alt="PyPI Version"><img src="https://img.shields.io/pypi/v/bfit?label=PyPI%20Version"/></a>
<img src="https://img.shields.io/pypi/format/bfit?label=PyPI%20Format"/>
<img src="https://img.shields.io/github/languages/code-size/dfujim/bfit"/>
<img src="https://img.shields.io/tokei/lines/github/dfujim/bfit"/>
<img src="https://img.shields.io/pypi/l/bfit"/>

<a href="https://github.com/dfujim/bfit/commits/master" alt="Commits"><img src="https://img.shields.io/github/commits-since/dfujim/bfit/latest/master"/></a>
<a href="https://github.com/dfujim/bfit/commits/master" alt="Commits"><img src="https://img.shields.io/github/last-commit/dfujim/bfit"/></a>

A Python application for the analysis of β-NMR and β-NQR data taken at TRIUMF. 

## Intent

β-detected nuclear magnetic resonance (β-NMR) is similar to muon spin rotation (μSR), using a radioactive atomic ion in the place of the muon. The bfit code has been written to aid β-NMR experimenters in their data analysis. 

The bfit GUI was written with the following goals: 

* Provide rapid, on-line analysis and feedback on data to inform descisions during beam time
* Allow for easy readback of file headers
* Enable data and results to be exported to a csv file
* Be user-friendly with a streamlined and intuitive operation
* Be maintainable enough to easily adapt to new run modes or spectometer features

whereas the goals for the API are:

* Easily allow for a high degree of sophistication and flexibility
* Provide accurate and reliable results
* Integrate well with [bdata](https://github.com/dfujim/bdata)

As a whole, the package should be easy to install to ease distribution.

## Useful links

* [Install instructions](https://github.com/dfujim/bfit/wiki/Installation-and-first-startup)
* [API](https://github.com/dfujim/bfit/wiki/API-Reference)
