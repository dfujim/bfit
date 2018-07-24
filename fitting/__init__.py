from fitting.ffreq import ffreq
from fitting.fpulsed import fpulsed

try:
    from fitting.integrator import PulsedFns
except ImportError:
    pass
