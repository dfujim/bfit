<!--
JOSS welcomes submissions from broadly diverse research areas. For this reason, we require that authors include in the paper some sentences that explain the software functionality and domain of use to a non-specialist reader. We also require that authors explain the research applications of the software. The paper should be between 250-1000 words.

Your paper should include:

    A list of the authors of the software and their affiliations, using the correct format (see the example below).
    A list of key references, including to other software addressing related needs. Note that the references should include full names of venues, e.g., journals and conferences, not abbreviations only understood in the context of a specific discipline.
    Mention (if applicable) a representative set of past or ongoing research projects using the software and recent scholarly publications enabled by it.
-->

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

<!---A summary describing the high-level functionality and purpose of the software for a diverse, non-specialist audience.--->
Beta-detected nuclear magnetic resonance ($\beta$-NMR) measures the beta-decay of probe radioactive nuclei to infer the electromagnetic character of the probe's local environment. Similar to muon spin rotation ($\mu$SR), this technique allows for unique insight of material properties not easily measured by conventional NMR. The [`bfit`] package provides a graphical user interface (GUI) and application programming interface (API) to facilitate the analysis of $\beta$-NMR measurements taken at TRIUMF.

# Background

$\beta$-NMR leverages the parity-violating nuclear weak interaction to measure the spin precession of a radioactive probe nucleus [@MacFarlane2015]. These nuclei can either be activated by neutrons or implanted as a foreign species as a low-energy particle beam. Upon decay, the direction of the emitted electron is correlated with the nuclear spin orientation. As with many nuclear and particle physics experiments, the data collected is the counted number of electrons emitted in a given direction. These counts are then histogrammed and processed to yield a signal of interest.

The activation or implantation of the probe nuclei require high-intensity particle beams, restricting the technique to large nationally-supported facilities. Even today, there are only a handful of locations capable of conducting $\beta$-NMR measurements, such as TRIUMF, situated in Vancouver, Canada. This facility has been running $\beta$-NMR experiments for the past 20 years, and has developed the Muon Data (MUD) file format [@Whidden1994] as a means of storing $\mu$SR and $beta$-NMR data.

# Statement of need

As with many older science applications, the MUD API is written in C and FORTRAN. These statically-typed and compiled languages are known for their computational efficiency, but may have a long development time relative to more modern languages. In many communities, scientific computing has shifted to languages such as Python: a dynamically-typed and interpreted language. As a result, Python has amassed a massive library of data analysis tools [@Virtanen2020]. The short development time of Python programs is particularly important in the context of scientific analysis, which are typically run only a few times by select individuals. As a result, the time taken to write the analysis code is a large part of the program's effective run time. The aim of this work is to bring this rapid prototyping style of analysis to $\beta$-NMR.

At TRIUMF, $\beta$-NMR receives approximately 5 weeks of beam time per year. As with other large-facility experiments employing particle beams, data is extremely limited and expensive to generate. Having the tools for on-line analysis is therefore crucial for efficient and informed measurement. 

It should be acknowledged that, while a large body of analysis software exists to support $\mu$SR workers (such as WIMDA [@Pratt2000], MANTID [@Arnold2014], and Musrfit [@Suter2012]), $\beta$-NMR does not have an extensive suite of maintained analysis programs. While there have been some recent improvements to this situation [@Saadaoui2018], the analysis required for any non-trivial $\beta$-NMR experiment necessitates the development of new code to meet the individual requirements of each experiment. While such code may employ Musrfit, which is compatible with the MUD file format, this approach may be cumbersome and presents a high entry barrier for students and visiting scientists. The package introduced here is very lightweight and intuitive. It also provides a simple interface to other Python packages, allowing for a great deal of flexibility and sophistication. Additionally, distribution through the [Python Package Index](https://pypi.org/project/bfit/) trivializes installation and maintenance by installing missing dependencies, updating packages, and providing a consistent method of version tracking. This is in stark contrast to another popularly used framework, ROOT [@Brun1997] which serves as the basis for Musrfit, and whose set up process can be quite involved.

# Usage

The [`bfit`] GUI has three primary functions which are contained in the _Inspect_, _Fetch_, and _Fit_ tabs. The purpose of the _Inspect_ tab (shown below) may be used to quickly view the file headers and plot the data in order to detect and solve problems as they may arise during measurement. The _Fetch_ tab has been designed to prepare the data for analysis, loading runs in batch and allowing the user to draw and compare each run. The _Fit_ tab provides the tools needed to fit a model to the data, and to view and analyze the result. These tools include global fitting (i.e., sharing fit parameters between data sets), constrained fitting (i.e., constraining a parameter to follow a specific model dependent on the experimental conditions, such as temperature), non-trivial fitting functions specific to pulsed-beam operation, multiple minimization routines, and more.

![The inspection tab of the [`bfit`] GUI.\label{fig:inspect}](inspect_tab.png){ width=80% }

While the GUI greatly facilitates rapid on-line analysis, the [`bfit`] API provides the flexibility needed for publishable analyses. The analysis tools and functions utilized in the GUI are readily accessible via the API, and documented in the [wiki].

# Acknowledgements

The author acknowledges the support of a SBQMI QuEST fellowship.

# References

[`bfit`]: https://github.com/dfujim/bfit
[wiki]: https://github.com/dfujim/bfit/wiki
