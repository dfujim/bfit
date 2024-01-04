# setup mud source library
integration_sources = [
    'DEIntegrationConstants.h',
    'DEIntegrator.h',
    'integration_fns.cpp',
    'integration_fns.h',
]

integration_lib = static_library('integration',
    integration_sources,
    override_options : ['cython_language=cpp'],
    )