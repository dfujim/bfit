# test inspect tab
# Derek Fujimoto
# Feb 2021

from bfit.test.testing import *
import numpy as np
from bfit.gui.calculator_nqr_B0 import calculator_nqr_B0

def test_calc():
    calc = calculator_nqr_B0(True)
    
    # voltage
    calc.current.set('1')
    calc.entry_current.focus_set()
    calc.calculate()
    test(float(calc.field.get()), 2.3878, "calculator nqr B0 set current = 1, compared to online calculator")
    
    # field
    calc.field.set('1')
    calc.entry_field.focus_set()
    calc.calculate()
    test(float(calc.current.get()), 0.3729, "calculator nqr B0 set field = 1, compared to online calculator")
