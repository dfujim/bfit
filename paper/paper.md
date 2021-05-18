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

The first $\mu$SR measurements were recorded in 1957 [@Garwin1957a]. The technique leverages the parity-violating nuclear weak interaction to measure the spin precession of the muon by its anisotropic beta decay, which is correlated with the spin direction. It was not long before these physical principles were applied to a population of probes composed of radioactive nuclei, instead of muons, and this new technique was named $\beta$-NMR.

The particle beams needed for $\mu$SR and $\beta$-NMR restrict these techniques to large nationally-supported facilities. Even today, there are only a handful of locations capable of producing the necessary high-intensities. One such facility is TRIUMF, situated in Vancouver, Canada. Instrumental in the early development of $\mu$SR [@Brewer2012], this facility developed the Muon Data (MUD) file format as a means of storing $\mu$SR data [@Whidden1994]. Given the similarities between the two techniques, this file format was naturally employed in service of $\beta$-NMR measurements at TRIUMF.

# Statement of need

As with many older science applications, the MUD API is written in C and FORTRAN. These statically-typed and compiled languages are known for their computational efficiency, but can be difficult to work with. This is perhaps one of the reasons why scientific computing has, in many communities, shifted to more modern languages such as Python: a dynamically-typed and interpreted language. As a result, Python has amassed a massive library of data analysis tools [@Virtanen2020, @McKinney2010]. The short development time of Python programs is particularly important in the context of scientific analysis, which are typically run only a few times by select individuals. As a result, the time taken to write the analysis code is a large part of the program's effective run time. The aim of this work is to bring this rapid prototyping style of analysis to $\beta$-NMR.

It should be acknowledged that, while a large body of analysis software exists to support $\mu$SR workers (such as WIMDA [@Pratt2000], MANTID [@Arnold2014], and Musrfit [@Suter2012]), $\beta$-NMR does not have an extensive suite of maintained analysis programs. While there have been some recent improvements to this situation [@Saadaoui2018] the analysis required for any non-trivial $\beta$-NMR experiment necessitates the development of new code to meet the individual requirements of each experiment. Such code may employ Musrfit, which is compatible with the MUD file format, but may be cumbersome and presents a high entry barrier for students and visiting scientists. The package introduced here is very lightweight, providing a simple interface to other Python packages, allowing for a great deal of flexibility and sophistication. This trivializes installation and maintenance by installing missing dependencies, updating packages, and providing a consistent method of version tracking. This is in stark contrast to another popularly used framework, ROOT [@Brun1997] which serves as the basis for Musrfit, and whose set up process can be quite involved.

# Usage

[`bfit`] has three primary functions which are contained in the tab _Inspect_, _Fetch_, and _Fit_. The purpose of the _Inspect_ tab (shown below) may be used to quickly view the file headers and plot the data in order to detect and solve problems as they may arise during measurement. The _Fetch_ tab has been designed to prepare the data for analysis, loading runs in batch and allowing the user to draw and compare each run. The _Fit_ tab provides the tools needed to fit a model to the data, and view and analyze the result.
![The inspection tab of the [`bfit`] GUI.\label{fig:inspect}](inspect_tab.png){ width=80% }

# Acknowledgements

The author acknowledges the support of a SBQMI QuEST fellowship.

# References


[`bfit`]: https://github.com/dfujim/bfit
