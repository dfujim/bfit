# test inspect tab
# Derek Fujimoto
# Feb 2021

from bfit.test.testing import *
import numpy as np

# get bfit object and tab
tab = b.fileviewer

def test_fetch(r, y, mode):    
    tab.year.set(y)
    tab.runn.set(r)
    test_action(tab.get_data, "fileviewer fetch %s (%d.%d) data" % (mode, y, r))
    test_perfect(tab.data.run, r, "fileviewer fetch %s (%d.%d) data accuracy" % (mode, y, r))
    
def test_draw(r, y, mode):
    
    # get data
    tab.year.set(y)
    tab.runn.set(r)
    tab.get_data()
    
    # draw
    n = len(tab.entry_asym_type['values'])
    
    for i in range(n):
        
        # switch draw types
        tab.entry_asym_type.current(i)
        draw_type = tab.asym_type.get()
        
        # draw
        test_action(tab.draw, "fileviewer draw %s in mode %s" % (mode, draw_type), 'inspect')
        
        if mode == '2e':
            b.do_close_all()
    
def test_autocomplete():
    tab.year.set(2020)
    tab.runn.set(402)
    tab.get_data()
    test_perfect(tab.data.run, 40299, 'fileviewer autocomplete fetch')
    

