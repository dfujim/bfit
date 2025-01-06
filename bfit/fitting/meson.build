# run subdirectories
subdir('FastNumericalIntegration_src')

# install cython packages

cy = meson.get_compiler('cython')
# generator() doesn't accept compilers, only found programs - cast it.
cython = find_program(cy.cmd_array()[0])

cython_args = ['--cplus', '-3', '--fast-fail', '--output-file', '@OUTPUT@', '--include-dir', '@BUILD_ROOT@', '@INPUT@']

cython_gen_cpp = generator(cython,
    arguments : cython_args,
    output : '@BASENAME@.cpp')

py.extension_module(
    'integrator',
    cython_gen_cpp.process('integrator.pyx'),
    install: true,
    dependencies: py_dep,
    include_directories: ['FastNumericalIntegration_src', incdir_numpy],
    subdir: 'bfit/fitting',
    link_with: [integration_lib],
    override_options: ['cython_version=3'],
    link_language: 'cpp'
)

# install python packages
python_sources = [
    'decay_31mg.py',
    'fit_bdata.py',
    'fitter.py',
    'fitter_curve_fit.py',
    'fitter_migrad_hesse.py',
    'fitter_migrad_minos.py',
    'functions.py',
    'gen_init_par.py',
    'global_bdata_fitter.py',
    'global_fitter.py',
    '__init__.py',
    'leastsquares.py',
    'minuit.py',
    '_scipy_misc.py',
]

py.install_sources(
    python_sources,
    subdir: 'bfit/fitting'
)
