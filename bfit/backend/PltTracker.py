# Track which plots are active, which to draw in. 
# Derek Fujimoto
# June 2019

import matplotlib.pyplot as plt

# =========================================================================== #
class PltTracker(object):
    """
        active:         dictionary, id number of active plot
        plots:          dictionary, list of plots drawn for type
    """
    
    # ======================================================================= #
    def __init__(self):
        
        # lists for tracking all plots 
        self.plots = {'data':[],'fit':[],'param':[],'periodic':[]}
        
        # track the active plot 
        self.active = {'data':0,'fit':0,'param':0,'periodic':0}
    
    # ======================================================================= #
    def _close_figure(self,event):
        """Remove figure from list"""
        
        # get number and style
        number = event.canvas.figure.number
        style = event.canvas.style
        
        # disconnect events
        event.canvas.mpl_disconnect(event.canvas.user_close)
        event.canvas.mpl_disconnect(event.canvas.user_active)
        
        # close the winow
        plt.figure(number).clf()
        plt.close(number)
        
        # remove from list 
        self.plots[style].remove(number)
        
        # reset active
        try:
            self.active[style] = self.plots[style][-1]
        except IndexError:
            self.active[style] = 0
                        
    # ======================================================================= #
    def _decorator(self,style,fn,*args,**kwargs):
        """
            Function wrapper
            
            style: one of "data", "fit", "param"
            fn: matplotlib function to operate on 
            args: passed to fn
            kwargs: passed to fn
        """
        
        # switch 
        plt.figure(self.active[style])

        # run function 
        output = fn(*args,**kwargs)
        
        return output
    
    # ======================================================================= #
    def _update_active_id(self,event):
        """
            Update the active figure id based on click event.
        """
        number = event.canvas.figure.number
        style = event.canvas.style
        self.active[style] = number
    
    # ======================================================================= #
    def annotate(self,style,*args,**kwargs):
        return self._decorator(style,plt.annotate,*args,**kwargs)
    
    # ======================================================================= #
    def axhline(self,style,*args,**kwargs):
        return self._decorator(style,plt.axhline,*args,**kwargs)
    
    # ======================================================================= #
    def axvline(self,style,*args,**kwargs):
        return self._decorator(style,plt.axvline,*args,**kwargs)
            
    # ======================================================================= #
    def clf(self,style):
        """Get the current axes for the style"""
        return self._decorator(style,plt.clf)
        
    # ======================================================================= # 
    def errorbar(self, style, x, y, yerr=None, xerr=None, fmt='', ecolor=None, 
                 elinewidth=None, capsize=None, barsabove=False, lolims=False, 
                 uplims=False, xlolims=False, xuplims=False, errorevery=1, 
                 capthick=None, *, data=None, **kwargs):
        """
            Plot data.
            
            style: one of "data", "fit", or "param"
            other arguments: defaults for matplotlib.pyplot.plot
        """
        
        # get active for this style
        active_style = self.active[style]
        
        # make new figure if needed 
        if active_style == 0:   
            self.figure(style)
            active_style = self.active[style]
        
        # draw in active style 
        plt.figure(active_style)
        obj = plt.errorbar(x, y, yerr=yerr, xerr=xerr, fmt=fmt, ecolor=ecolor, 
                     elinewidth=elinewidth, capsize=capsize, 
                     barsabove=barsabove, lolims=lolims, uplims=uplims, 
                     xlolims=xlolims, xuplims=xuplims, errorevery=errorevery, 
                     capthick=capthick, data=data, **kwargs)
        
        return obj
    
    # ======================================================================= #
    def figure(self,style,**kwargs):
        """
            Make new figure.
            
            style: one of "data", "fit", or "param"
            kwargs: keyword arguments to pass to plt.figure
        """
        
        # make figure
        fig = plt.figure(**kwargs)
        
        # make events and save as canvas attribute
        fig.canvas.user_close = fig.canvas.mpl_connect('close_event', self._close_figure)
        fig.canvas.user_active = fig.canvas.mpl_connect('button_press_event', self._update_active_id)
        
        # set style
        fig.canvas.style = style
        
        # set window name 
        fig.canvas.set_window_title('Figure %d (%s)' % (fig.number,style.title()))
        
        # update lists
        self.plots[style].append(fig.number)
        self.active[style] = fig.number
        
        return fig

    # ======================================================================= #
    def gca(self,style):
        if not self.plots[style]: self.figure(style)
        return self._decorator(style,plt.gca)
    
    # ======================================================================= #
    def gcf(self,style):
        if not self.plots[style]: self.figure(style)
        return self._decorator(style,plt.gcf)
    
    # ======================================================================= #
    def legend(self,style,*args,**kwargs):
        self._decorator(style,plt.legend,*args,**kwargs)
        
    # ======================================================================= #
    def plot(self,style, *args, scalex=True, scaley=True, data=None, **kwargs):
        """
            Plot data.
            
            style: one of "data", "fit", or "param"
            other arguments: defaults for matplotlib.pyplot.plot
        """
        
        # get active for this style
        active_style = self.active[style]
        
        # make new figure if needed 
        if active_style not in self.plots[style]:   
            self.figure(style)
        
        # draw in active style 
        plt.figure(active_style)
        obj = plt.plot(*args,scalex=scalex, scaley=scaley, data=data,**kwargs)
        
        return obj

    # ======================================================================= #
    def text(self,style,*args,**kwargs):
        return self._decorator(style,plt.text,*args,**kwargs)

    # ======================================================================= #
    def tight_layout(self,style,*args,**kwargs):
        return self._decorator(style,plt.tight_layout,*args,**kwargs)

    # ======================================================================= #
    def xlabel(self,style,*args,**kwargs):
        return self._decorator(style,plt.xlabel,*args,**kwargs)
    
    # ======================================================================= #
    def xlim(self,style,*args,**kwargs):
        return self._decorator(style,plt.xlim,*args,**kwargs)
    
    # ======================================================================= #
    def xticks(self,style,*args,**kwargs):
        return self._decorator(style,plt.xticks,*args,**kwargs)
    
    # ======================================================================= #
    def ylabel(self,style,*args,**kwargs):
        return self._decorator(style,plt.ylabel,*args,**kwargs)
    
    # ======================================================================= #
    def ylim(self,style,*args,**kwargs):
        return self._decorator(style,plt.ylim,*args,**kwargs)
    
    # ======================================================================= #
    def yticks(self,style,*args,**kwargs):
        return self._decorator(style,plt.yticks,*args,**kwargs)
    
    # ======================================================================= #
    def zlabel(self,style,*args,**kwargs):
        return self._decorator(style,plt.zlabel,*args,**kwargs)
    
    # ======================================================================= #
    def zlim(self,style,*args,**kwargs):
        return self._decorator(style,plt.zlim,*args,**kwargs)
    
    # ======================================================================= #
    def zticks(self,style,*args,**kwargs):
        return self._decorator(style,plt.zticks,*args,**kwargs)
    
