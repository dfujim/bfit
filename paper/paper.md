---
title: 'bfit: A Python Application For Beta-Detected NMR'
tags:
  - Python
  - beta-detected NMR
authors:
  - name: Derek Fujimoto
    orcid: 0000-0003-2847-2053
    affiliation: "1,2"
affiliations:
 - name: Stewart Blusson Quantum Matter Institute, University of British Columbia, Vancouver, BC V6T 1Z4, Canada
   index: 1
 - name: Department of Physics and Astronomy, University of British Columbia, Vancouver, BC V6T 1Z1, Canada
   index: 2
date: 17 May 2021
bibliography: paper.bib
---

# Summary

Beta-detected nuclear magnetic resonance ($\beta$-NMR) measures the beta-decay of probe radioactive nuclei to infer the electromagnetic character of the probe's local environment. Similar to muon spin rotation ($\mu$SR), this technique allows for unique insight of material properties not easily measured by conventional NMR. The [`bfit`] package provides a graphical user interface (GUI) and application programming interface (API) to facilitate the analysis of implanted-ion $\beta$-NMR measurements taken at TRIUMF.

# Background

$\beta$-NMR leverages the parity-violating nuclear weak interaction to measure the spin precession of a ensemble of radioactive probe nuclei [@MacFarlane2015]. These nuclei can either be activated by neutrons or implanted as a foreign species in the form of a low-energy particle beam. Upon decay, the direction of the emitted electron is correlated with the nuclear spin orientation. As with many nuclear and particle physics experiments, the data collected is the counted number of electrons emitted in a given direction. These counts are then histogrammed and processed to yield a signal of interest.

The activation or implantation of the probe nuclei require high-intensity particle beams, restricting the technique to large nationally-supported facilities. Even today, there are only a handful of locations capable of conducting $\beta$-NMR measurements, such as TRIUMF, which is situated in Vancouver, Canada. This facility has been running $\beta$-NMR experiments for the past 20 years, and has developed the Muon Data (MUD) file format [@Whidden1994] as a means of storing $\mu$SR and $\beta$-NMR data.

# Statement of need

At TRIUMF, $\beta$-NMR receives approximately 5 weeks of radioactive beam time per year. As with other large-facility experiments employing particle beams, this data is extremely limited and expensive to generate. Having the tools for rapid on-line analysis is therefore crucial for efficient and informed measurement. Additionally, many of the experimenters using the $\beta$-NMR spectrometer are visiting scientists or students who have little experience with the technical aspects of the measurement.

As with many older science applications, the MUD API is written in C and FORTRAN. These statically-typed and compiled languages are known for their computational efficiency, but are accompanied by long development times, relative to modern languages. In many communities, scientific computing has shifted to languages such as Python: a dynamically-typed and interpreted language. As a result, Python has amassed a massive library of data analysis tools [@Virtanen2020]. The short development time of Python programs is particularly important in the context of scientific analyses, which are typically run only a few times by select individuals. As a result, the development time of the analysis code comprises a large part of the program's effective run time. The aim of this work is to bring this rapid prototyping style of analysis to $\beta$-NMR. To further streamline on-line analyses, [`bfit`] provides an intuitive GUI capable of a moderately high degree of sophistication.

It should be acknowledged that, while a large body of analysis software exists to support $\mu$SR workers (such as WIMDA [@Pratt2000], MANTID [@Arnold2014], and Musrfit [@Suter2012]), $\beta$-NMR does not have a comparably extensive suite of maintained analysis programs. While there have been some recent improvements to this situation [@Saadaoui2018], the analysis required for any non-trivial $\beta$-NMR experiment necessitates the development of new code to meet the individual requirements of each experiment. While such code may employ Musrfit, which is compatible with the MUD file format, this approach may be cumbersome for complex or rapid analyses, and presents a entry high entry barrier for new users. The Python API of [`bfit`] is well suited for addressing these issues.

# Usage and features

The [`bfit`] GUI has three primary functions which are contained in the _Inspect_, _Fetch_, and _Fit_ tabs. The purpose of the _Inspect_ tab (shown below) is to quickly view the file headers and plot the data in order to detect and solve problems as they may arise during measurement. The _Fetch_ tab has been designed to prepare the data for analysis, loading runs in batch and allowing the user to draw and compare each run. The _Fit_ tab provides the tools needed to fit a model to the data, and to view and analyze the result. These tools include global fitting (i.e., sharing fit parameters between data sets), constrained fitting (i.e., constraining a parameter to follow a specific model dependent on the experimental conditions, such as temperature), non-trivial fitting functions specific to pulsed-beam operation (leveraging double exponential integration [@Cook2014]), multiple minimization routines, and more.

![The inspection tab of the `bfit` GUI.](inspect_tab.png){ width=80% }

While the GUI greatly facilitates rapid on-line analysis, the [`bfit`] API provides the flexibility needed for publishable analyses. The analysis tools and functions utilized in the GUI are readily accessible via the API, and documented in the [wiki]. Many of these tools are very general, easily interfacing with other Python packages, and can accommodate a great deal of complexity and sophistication.

# Acknowledgements

The author would like to thank the members of the $\beta$-NMR group at TRIUMF for their useful input and feedback. In particular, discussions with R. M. L. McFadden have been particularly useful. The author additionally acknowledges the support of a SBQMI QuEST fellowship.

# References

[`bfit`]: https://github.com/dfujim/bfit
[wiki]: https://github.com/dfujim/bfit/wiki
