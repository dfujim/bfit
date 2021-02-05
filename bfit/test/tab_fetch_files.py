# test inspect tab
# Derek Fujimoto
# Feb 2021

from bfit.test.testing import *
import numpy as np
import matplotlib.pyplot as plt

# get bfit object and tab
tab = b.fetch_files
b.notebook.select(1)

def test_fetch():
    
    # set year
    tab.year.set(2020)
    
    # get one
    tab.run.set('40123')
    tab.get_data()
    test_perfect(len(list(tab.data_lines.keys())), 1, 'fetch tab fetch single run')
    
    tab.run.set('40124')
    tab.get_data()
    test_perfect(len(list(tab.data_lines.keys())), 2, 'fetch tab fetch another single run')
    
    # get two
    tab.run.set('40125 40126')
    tab.get_data()
    test_perfect(len(list(tab.data_lines.keys())), 4, 'fetch tab fetch run list')
    
    # get range
    tab.run.set('40127-40129')
    tab.get_data()
    test_perfect(len(list(tab.data_lines.keys())), 7, 'fetch tab fetch run range')
    
def test_remove():
    
    # get some data
    tab.year.set(2020)
    tab.run.set('40123-40130')
    tab.get_data()
    
    # remove single
    tab.data_lines['2020.40123'].degrid()
    test_perfect(len(list(tab.data_lines.keys())), 7, 'fetch tab remove single')
    
    # remove all
    tab.remove_all()
    test_perfect(len(list(tab.data_lines.keys())), 0, 'fetch tab remove all')
    
def test_checkbox():
    
    # get some data
    tab.year.set(2020)
    tab.run.set('40123-40126')
    tab.get_data()
    
    # force check
    tab.check_state.set(False)
    tab.check_all()
    
    test_perfect(all([d.check_state.get() is False for d in tab.data_lines.values()]), True, 'fetch tab force check')
    
    tab.check_state.set(True)
    tab.check_all()
    
    # uncheck one then uncheck data
    tab.data_lines['2020.40123'].check_state.set(False)
    
    tab.check_state_data.set(False)
    tab.check_all_data()
    
    test_perfect(tab.data_lines['2020.40123'].check_data.get(), True, 'fetch tab check data on unchecked item')
    test_perfect(tab.data_lines['2020.40124'].check_data.get(), False, 'fetch tab check data on checked item')
    
    # test check toggle
    tab.toggle_all()
    test_perfect(tab.data_lines['2020.40123'].check_state.get(), True, 'fetch tab toggle check False -> True')
    test_perfect(tab.data_lines['2020.40124'].check_state.get(), False, 'fetch tab toggle check True -> False')
    
    
    tab.remove_all()
    
def test_draw():
    
    # get some data
    tab.year.set(2020)
    tab.run.set('40123-40126')
    tab.get_data()
    
    # draw stack
    b.draw_style.set('stack')
    tab.draw_all('data')
    ax = plt.gca()
    test_perfect(len(ax.draw_objs), 4, 'fetch tab draw all stack')
    
    tab.run.set('40127-40128')
    tab.get_data()
    tab.draw_all('data')
    test_perfect(len(ax.draw_objs), 6, 'fetch tab draw all stack with more data')
    
    # draw new
    b.draw_style.set('new')
    tab.draw_all('data')
    test_perfect(len(b.plt.plots['data']), 2, 'fetch tab draw all new')
    
    # draw redraw
    b.draw_style.set('redraw')
    tab.remove_all()
    tab.run.set('40127-40128')
    tab.get_data()
    tab.draw_all('data')
    test_perfect(len(plt.gca().draw_objs), 2, 'fetch tab draw all redraw')

    b.do_close_all()
