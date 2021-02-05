# test inspect tab
# Derek Fujimoto
# Feb 2021

from bfit.test.testing import *
import numpy as np
import matplotlib.pyplot as plt

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
    
def test_draw_mode():
    
    tab.year.set(2020)
    
    # test stack
    b.draw_style.set('stack')
    
    tab.runn.set(40123)
    tab.get_data()
    tab.entry_asym_type.current(0) # set combined asym mode
    
    tab.draw('inspect')
    
    tab.runn.set(40127)
    tab.get_data()
    tab.draw('inspect')
    
    ax = plt.gca()
    test_perfect(len(ax.draw_objs), 2, 'fileviewer stack')
    
    # test redraw
    b.draw_style.set('redraw')
    
    tab.runn.set(40123)
    tab.get_data()
    tab.entry_asym_type.current(0) # set combined asym mode
    
    tab.draw('inspect')
    
    tab.runn.set(40127)
    tab.get_data()
    tab.draw('inspect')
    
    ax = plt.gca()
    test_perfect(len(ax.draw_objs), 1, 'fileviewer redraw')
    
    # test new
    b.draw_style.set('new')
    
    tab.runn.set(40123)
    tab.get_data()
    tab.entry_asym_type.current(0) # set combined asym mode
    
    tab.draw('inspect')
    tab.draw('inspect')
    
    test_perfect(len(b.plt.plots['inspect']), 3, 'fileviewer draw new')
    
    b.do_close_all()
    
def test_autocomplete():
    tab.year.set(2020)
    tab.runn.set(402)
    tab.get_data()
    test_perfect(tab.data.run, 40299, 'fileviewer autocomplete fetch')
    

