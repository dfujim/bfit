from bfit.fitting.continuous import fscan

try:
    from bfit.fitting.integrator import PulsedFns
except ImportError:
    print("\n integrator not compiled. From withing bfit/fitting/, call: "+\
          "'python3 setup_integrator.py build_ext --inplace'")
else:
    from bfit.fitting.pulsed import slr


from bfit.fitting.default_routines import fitter
