# Define some global variables needed for setup
# Derek Fujimoto
# Aug 2021

from os.path import join

__src__ = join('bfit', 'fitting')
__version__ = '4.14.0'

# keywords used to identify variables
KEYVARS = { 'B0'    : 'B0 Field (T)', 
            'BIAS'  : 'Platform Bias (kV)', 
            'CLFT'  : 'Cryo Lift Read (mm)', 
            'DUR'   : 'Run Duration (s)', 
            'ENRG'  : 'Impl. Energy (keV)', 
            'LAS'   : 'Laser Power (V)', 
            'NBMR'  : 'NBM Rate (count/s)', 
            'RATE'  : 'Sample Rate (count/s)', 
            'RF'    : 'RF Level DAC', 
            'RUN'   : 'Run Number', 
            'TEMP'  : 'Temperature (K)', 
            'TIME'  : 'Start Time', 
            'YEAR'  : 'Year', 
          }    
