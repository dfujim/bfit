# test inspect tab
# Derek Fujimoto
# Feb 2021

from bfit.test.testing import *
import numpy as np
from bfit.gui.calculator_nmr_B1 import calculator_nmr_B1

def test_calc():
    calc = calculator_nmr_B1(True)
    
    # voltage
    calc.volt.set('1')
    calc.entry_voltage.focus_set()
    calc.calculate()
    test(float(calc.field.get()), 0.000960, "calculator nmr B1 set volt = 1")
    
    # field
    calc.field.set('1')
    calc.entry_field.focus_set()
    calc.calculate()
    test(float(calc.volt.get()), 1042.171717, "calculator nmr B1 set field = 1")
