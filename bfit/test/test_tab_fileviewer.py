# test inspect tab
# Derek Fujimoto
# Feb 2021

from numpy.testing import *
import numpy as np
import matplotlib.pyplot as plt
from bfit.gui.bfit import bfit

# make gui
b = bfit(None, True)

# get bfit object and tab
tab = b.fileviewer

def test_fetch_20():    fetch(40123, 2020, '20')
def test_fetch_1f():    fetch(40033, 2020, '1f')
def test_fetch_1w():    fetch(40037, 2020, '1w')
def test_fetch_1n():    fetch(40011, 2020, '1n')
def test_fetch_2h():    fetch(45539, 2019, '2h')
def test_fetch_2e():    fetch(40326, 2019, '2e')
def test_draw_20():     draw(40123, 2020, '20')
def test_draw_1f():     draw(40033, 2020, '1f')
def test_draw_1w():     draw(40037, 2020, '1w')
def test_draw_1n():     draw(40011, 2020, '1n')
def test_draw_2h():     draw(45539, 2019, '2h')
def test_draw_2e():     draw(40326, 2019, '2e')

def fetch(r, y, mode):    
    tab.year.set(y)
    tab.runn.set(r)
    
    try:
        tab.get_data()
    except Exception as err: 
        print(err)
        raise AssertionError("fileviewer fetch %s (%d.%d) data" % (mode, y, r))
    
    assert_equal(tab.data.run, r, "fileviewer fetch %s (%d.%d) data accuracy" % (mode, y, r))
    
def draw(r, y, mode):
    
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
        try:
            tab.draw(figstyle = 'inspect')
        except Exception as err: 
            print(err)
            raise AssertionError("fileviewer draw %s in mode %s" % (mode, draw_type), 'inspect')
        
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
    assert_equal(len(ax.draw_objs), 2, 'fileviewer stack')
    
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
    assert_equal(len(ax.draw_objs), 1, 'fileviewer redraw')
    
    # test new
    b.draw_style.set('new')
    
    tab.runn.set(40123)
    tab.get_data()
    tab.entry_asym_type.current(0) # set combined asym mode
    
    tab.draw('inspect')
    tab.draw('inspect')
    
    assert_equal(len(b.plt.plots['inspect']), 3, 'fileviewer draw new')
    
    b.do_close_all()
    
def test_autocomplete():
    tab.year.set(2020)
    tab.runn.set(402)
    tab.get_data()
    assert_equal(tab.data.run, 40299, 'fileviewer autocomplete fetch')
    

