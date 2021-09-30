# bfit

<a href="https://pypi.org/project/bfit/" alt="PyPI Version"><img src="https://img.shields.io/pypi/v/bfit?label=PyPI%20Version"/></a>
<img src="https://img.shields.io/pypi/format/bfit?label=PyPI%20Format"/>
<img src="https://img.shields.io/github/languages/code-size/dfujim/bfit"/>
<img src="https://img.shields.io/tokei/lines/github/dfujim/bfit"/>
<img src="https://img.shields.io/pypi/l/bfit"/>
[![DOI](https://joss.theoj.org/papers/10.21105/joss.03598/status.svg)](https://doi.org/10.21105/joss.03598)

<a href="https://github.com/dfujim/bfit/commits/master" alt="Commits"><img src="https://img.shields.io/github/commits-since/dfujim/bfit/latest/master"/></a>
<a href="https://github.com/dfujim/bfit/commits/master" alt="Commits"><img src="https://img.shields.io/github/last-commit/dfujim/bfit"/></a>

[bfit] is a [Python] application aimed to aid in the analysis of β-detected
nuclear magnetic/quadrupole resonance (β-NMR and β-NQR) data taken at [TRIUMF].
These techniques are similar to muon spin rotation ([μSR]) and "conventional"
nuclear magnetic resonance ([NMR]), but use radioactive nuclei as their [NMR]
probe in place of the [muon] or a stable isotope.
The instruments and research program are governed through [TRIUMF]'s [CMMS],
with more information given at <https://bnmr.triumf.ca>.
An overview of instrumentation details and scientific applications of the
β-NMR/β-NQR techniques can be found in several recent journal articles:

- W. A. MacFarlane.
  <i>Implanted-ion βNMR: a new probe for nanoscience</i>.
  <a href="https://doi.org/10.1016/j.ssnmr.2015.02.004">
  Solid State Nucl. Magn. Reson. <b>68-69</b>, 1-12 (2015)</a>.
- G. D. Morris.
  <i>β-NMR</i>.
  <a href="https://doi.org/10.1007/s10751-013-0894-6">
  Hyperfine Interact. <b>225</b>, 173-182 (2014)</a>.

The intended user of [bfit] is anyone performing experiments with or analyzing
data taken from [TRIUMF]'s β-NMR or β-NQR spectrometers - independent of whether
they are a new student, visiting scientist, or someone with decades of experience.
(e.g., someone from the "local" [TRIUMF]/[CMMS]/[UBC] group).
A key goal of the project is to alleviate much of the technical tedium that is
often encountered during any analysis.
More generally, [bfit] has been written to fulfill the following needs:

* Provide the means for quick on-line analyses during beam time.
* Provide a useful and flexible API for refined analyses in [Python],
  to be used in conjunction with [bdata] and the [SciPy] ecosystem.
* Provide an intuitive, user-friendly interface for non-programmers.
* Be easily maintainable and distributable.

## Citing

If you use [bfit] in your work, please cite:

D. Fujimoto, "bfit: A Python Application For Beta-Detected NMR," [J. Open Source Softw. <b>6</b>, 3598 (2021).](https://doi.org/10.21105/joss.03598)

## Useful Links

* [bfit]
  * [Wiki]
    * [API Reference]
    * [API Tutorial]
    * [GUI Tutorial]
* [mudpy]
* [bdata]

## Community Guidelines

* Contributing:
  * Please submit your contribution to [bfit] through the list of
    [Pull Requests]!
* Reporting issues and/or seeking support:
  * Please file a new ticket in [bfit]'s list of [Issues] - I will get an email
    notification of your problem and try to fix it ASAP!

## Installation and Use

### Dependencies

The following packages/applications are needed _prior_ to [bfit] installation:
- [Python] 3.6 or higher: a dynamically typed programming language. [[install](https://wiki.python.org/moin/BeginnersGuide/Download)]
- [Tkinter] : [Python]'s de facto standard GUI package. [[install](https://tkdocs.com/tutorial/install.html)]

### Install Instructions

|  | Command |
|:-- | :--|
From the [PyPI] as user (recommended) | `pip install --user bfit` |
From the [PyPI] as root | `pip install bfit` |
From source | `python3 setup.py install` |

Note that `pip` should point to a (version 3) [Python] executable
(e.g., `python3`, `python3.8`, etc.).
If the above does not work, try using `pip3` or `python3 -m pip` instead.

### Optional Setup

For convenience,
you may want to tell [bfit] where the data is stored on your machine.
This is done by defining two environment variables:
`BNMR_ARCHIVE` and `BNQR_ARCHIVE`.
This can be done, for example, in your `.bashrc` script.
Both variables expect the data to be stored in directories with a particular
heirarchy:

```
/path/
|---bnmr/
|---bnqr/
|-------2017/
|-------2018/
|-----------045123.msr
```

Here, the folders `/path/bnmr/` and `/path/bnqr/` both contain runs
(i.e., `.msr` files) organized into subdirectories by year of aquasition.
In this case, you would set (in your `.bashrc`):

```bash
export BNMR_ARCHIVE=/path/bnmr/
export BNQR_ARCHIVE=/path/bnqr/
```

If [bfit] cannot find the data, it will attempt to download the relavent [MUD]
(i.e., `.msr`) files from <https://cmms.triumf.ca/mud/runSel.html>.
This is the default behaviour for [bfit] installed from [PyPI].

### First Startup 

To launch the GUI from a terminal simply call `bfit`, if this fails, one can also use the alternative syntax `python3 -m bfit`, where `python3` may be replaced with any (version 3) [Python] executable.

### Testing

Testing your installation of [bfit] is accomplished by running `pytest` within the installation folder. Note that some tests, particularly those involving drawing, fail when run as group in this environment, but they should pass on a subsequent attempts: `pytest --lf`. Further testing information can be found [here](https://github.com/dfujim/bfit/wiki/Installation-and-first-startup).

[Python]: https://www.python.org/
[SciPy]: https://www.scipy.org/
[Cython]: https://cython.org/
[NumPy]: https://numpy.org/
[pandas]: https://pandas.pydata.org/
[Matplotlib]: https://matplotlib.org/
[Tkinter]: https://wiki.python.org/moin/TkInter
[PyYAML]: https://pyyaml.org/
[pytest]: https://docs.pytest.org/en/6.2.x/
[tqdm]: https://github.com/tqdm/tqdm
[requests]: https://requests.readthedocs.io/en/master/
[Jupyter]: https://jupyter.org/
[argparse]: https://docs.python.org/3/library/argparse.html

[YAML]: https://yaml.org/
[C]: https://en.wikipedia.org/wiki/C_(programming_language)
[HTTP]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol

[TRIUMF]: https://www.triumf.ca/
[CMMS]: https://cmms.triumf.ca
[MUD]: https://cmms.triumf.ca/mud/
[archive]: https://cmms.triumf.ca/mud/runSel.html
[`data/BNMR/2020/040123.msr`]: https://cmms.triumf.ca/mud/mud_hdrs.php?ray=Run%2040123%20from%20BNMR%20in%202020&cmd=heads&fn=data/BNMR/2020/040123.msr

[PHYSICA]: https://computing.triumf.ca/legacy/physica/
[UBC]: https://www.ubc.ca/
[μSR]: https://en.wikipedia.org/wiki/Muon_spin_spectroscopy
[NMR]: https://en.wikipedia.org/wiki/Nuclear_magnetic_resonance
[muon]: https://en.wikipedia.org/wiki/Muon

[bnmr_1f]: https://gitlab.com/rmlm/bnmr_1f
[bnmr_2e]: https://gitlab.com/rmlm/bnmr_2e
[bnmrfit]: https://gitlab.com/rmlm/bnmrfit
[bnmroffice]: https://github.com/hsaadaoui/bnmroffice
[musrfit]: https://bitbucket.org/muonspin/musrfit
[musrfit documentation]: https://lmu.web.psi.ch/musrfit/user/html/index.html

[mudpy]: https://github.com/dfujim/mudpy
[bdata]: https://github.com/dfujim/bdata

[bfit]: https://github.com/dfujim/bfit
[Pull Requests]: https://github.com/dfujim/bfit/pulls
[Issues]: https://github.com/dfujim/bfit/issues
[PyPI]: https://pypi.org/project/bfit/
[API Reference]: https://github.com/dfujim/bfit/wiki/API-Reference
[API Tutorial]: https://github.com/dfujim/bfit/wiki/API-Tutorial
[GUI Tutorial]: https://github.com/dfujim/bfit/wiki/GUI-Tutorial
[Wiki]: https://github.com/dfujim/bfit/wiki

[ROOT]: https://github.com/root-project/root
[MINUIT]: https://doi.org/10.1016/0010-4655(75)90039-9
[MINUIT2]: https://root.cern/doc/master/Minuit2Page.html
[iminuit]: https://github.com/scikit-hep/iminuit
