# move the working plot to the top and focus on it
# Derek Fujimoto
# July 2019 

import matplotlib.pyplot as plt

# bring window to front
def raise_window():
    wm = plt.get_current_fig_manager()
    
    wm.window.attributes('-topmost', True)
    wm.window.attributes('-topmost', False)
    wm.canvas.get_tk_widget().focus_force()
