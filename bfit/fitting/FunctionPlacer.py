# Put a function on the active plot and adjust it's parameters with mouse buttons
# Derek Fujimoto
# April 2019

import bdata as bd
import matplotlib.pyplot as plt
import numpy as np
from bfit.fitting.functions import lorentzian # freq, peak, width, amp
from bfit.fitting.functions import pulsed_exp # time, lambda_s, amp
from bfit.fitting.functions import pulsed_strexp # time, lambda_s, beta, amp

class FunctionPlacer(object):
    
    npts = 500  # number of points used to draw line
    tau = bd.life.Li8   # lifetime of probe 
    
    # ======================================================================= #
    def __init__(self,fig,data,fn,p0):
        """
            fn needs input parameters with keys: 
            
                1F
                    peak,width,amp,base
                20/2H
                    amp,lam,beta (optional), base (optional)
        """
        # save input
        self.fig = fig
        self.fn = fn
        self.p0_variable = p0
        self.p0 = {k:float(p0[k].get()) for k in p0.keys()}
        
        self.mode = data.mode
        x = data.asym('c')[0]
        self.x = np.linspace(min(x),max(x),self.npts)
        
        # get pulse length
        # ~ if self.mode in ('20','2h'):
            # ~ self.pulse = data.get_pulse_s()
        
        # get axes for drawing
        self.ax = fig.axes
        if len(self.ax) == 0:
            self.ax = fig.add_subplot(111)
        else:
            self.ax = self.ax[0]
        
        # draw line with initial parameters
        self.line = self.ax.plot(self.x,fn(self.x,**self.p0,),zorder=20)[0]
        
        # start step
        self.step = 0
        
        # inital connect
        if self.mode in ('20','2h'):    self.connect_motion_20()
        elif self.mode in ('1f',):      self.connect_motion_1f()
        self.connect_click()
    
    # ======================================================================= #
    def connect_click(self):
        """Connect the mouse release events"""
        
        if self.mode in ('1f',):
            self.cidrelease = self.line.figure.canvas.mpl_connect(
                'button_release_event',self.connect_motion_1f)
        elif self.mode in ('20','2h'):
            self.cidrelease = self.line.figure.canvas.mpl_connect(
                'button_release_event',self.connect_motion_20)
        else:
            pass
            
    # ======================================================================= #
    def connect_motion_20(self,*args):
        """Connect the needed mouse motion events"""
        
        if self.step == 0:
            
            titlestr = ''
            
            # do baseline, if it exists    
            if 'base' in self.p0.keys():
                self.cidmotion_y = self.line.figure.canvas.mpl_connect(
                    'motion_notify_event', self.on_motion_20base)
                titlestr += 'base (ymove), '
                    
            # do T1
            self.cidmotion_x = self.line.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion_20lam)
            titlestr += '1/T1 (xmove)'
            
            # do initial asymmetry
            self.cidscroll = self.line.figure.canvas.mpl_connect(
                    'scroll_event', self.on_scroll_20amp)
            titlestr += ', amp (scroll)'
            
            # do beta
            if 'beta' in self.p0.keys():
                self.cidkey = self.line.figure.canvas.mpl_connect(
                    'key_press_event', self.on_key_20beta)
                titlestr += ', beta (arrow keys)'
            
            self.ax.set_title(titlestr,fontsize='small')
            
        # END: disconnect
        else:
            
            if hasattr(self,'cidmotion_x'):   
                self.line.figure.canvas.mpl_disconnect(self.cidmotion_x)
            if hasattr(self,'cidmotion_y'):   
                self.line.figure.canvas.mpl_disconnect(self.cidmotion_y)
            if hasattr(self,'cidscroll'):   
                self.line.figure.canvas.mpl_disconnect(self.cidscroll)
            if hasattr(self,'cidkey'):   
                self.line.figure.canvas.mpl_disconnect(self.cidscroll)
            self.line.figure.canvas.mpl_disconnect(self.cidrelease)
            
            self.ax.set_title('')
            for k in self.p0.keys():
                self.p0_variable[k].set(str(self.p0[k]))
        self.step += 1
        self.fig.show()
    
    # ======================================================================= #
    def connect_motion_1f(self,*args):
        """Connect the needed mouse motion events"""
        
        # connect motion to setting the peak
        if self.step == 0:

            self.ax.set_title('Click to set peak position',fontsize='small')
            self.cidmotion = self.line.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion_1fpeak)
        
        # connect motion to setting the base
        elif self.step == 1:
            
            self.ax.set_title('Click to set baseline',fontsize='small')
            self.line.figure.canvas.mpl_disconnect(self.cidmotion)
            self.cidmotion = self.line.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion_1fbase)
                
         # connect motion to setting the width
        elif self.step == 2:
            
            self.ax.set_title('Click to set width',fontsize='small')
            self.line.figure.canvas.mpl_disconnect(self.cidmotion)
            self.cidmotion = self.line.figure.canvas.mpl_connect(
                'motion_notify_event', self.on_motion_1fwidth)
            
        # END: disconnect
        else:
            self.ax.set_title('')
            self.line.figure.canvas.mpl_disconnect(self.cidmotion)
            self.line.figure.canvas.mpl_disconnect(self.cidrelease)
            for k in self.p0.keys():
                self.p0_variable[k].set(str(self.p0[k]))
            
        self.step += 1
    
    # ======================================================================= #
    def on_motion_20base(self,event):
        """Updated the baseline on mouse movement"""
        
        # check event data
        if event.ydata is not None:
            
            self.p0['base'] = event.ydata
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
     
    # ======================================================================= #
    def on_scroll_20amp(self,event):
        """Updated the initial asymmetry on mouse movement"""
     
        # check event data
        if event.step is not None:
            
            self.p0['amp'] += self.p0['amp']*0.05*event.step
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
 
    # ======================================================================= #
    def on_key_20beta(self,event):
        """Updated the initial asymmetry on mouse movement"""
     
        beta = self.p0['beta']
     
        # check event data
        if event.key in ('up','right'):
            beta += beta*0.05
            
        elif event.key in ('down','left'):
            beta -= beta*0.05            
        else:
             return

        self.p0['beta'] = min(max(beta,0),1)
        self.line.set_ydata(self.fn(self.x,**self.p0))
        self.line.figure.canvas.draw()
        
    # ======q================================================================= #
    def on_motion_20lam(self,event):
        """Updated 1/T1 on mouse movement"""
        
        # set lambda
        if event.xdata is not None:
            self.p0['lam'] = 1/(event.xdata*2)
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
                
    # ======================================================================= #
    def on_motion_1fpeak(self,event):
        """Updated the peak position on mouse movement"""
        
        # check event data
        if event.xdata is not None and event.ydata is not None:
            
            self.p0['peak'] = event.xdata
            self.p0['base'] = event.ydata+self.p0['amp']
            
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
        
    # ======================================================================= #
    def on_motion_1fbase(self,event):
        """Updated the baseline position on mouse movement"""
        
        # check event data
        if event.xdata is not None and event.ydata is not None:
            
            self.p0['amp'] -= self.p0['base']-event.ydata
            self.p0['base'] = event.ydata
            
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
    
    # ======================================================================= #
    def on_motion_1fwidth(self,event):
        """Updated the width on mouse movement"""
        
        # check event data
        if event.xdata is not None and event.ydata is not None:
            
            self.p0['width'] = abs(self.p0['peak']-event.xdata)
            self.line.set_ydata(self.fn(self.x,**self.p0))
            self.line.figure.canvas.draw()
        
# RUN ======================================================================= #

# get and draw data
# ~ fig = plt.figure()

# 1F version
# ~ data = bd.bdata(40142,2018)
# ~ fn = lambda freq,peak,width,amp,base : lorentzian(freq,peak,width,amp) + base
# ~ p0 = {'peak':43075800,'width':3200,'amp':0.032,'base':0.04}

# SLR version - normal exp
# ~ data = bd.bdata(40123,2018)
# ~ pexp = pulsed_exp(lifetime=bd.life.Li8,pulse_len=data.get_pulse_s())
# ~ fn = lambda time,lam,amp,base : pexp(time,lam,amp) + base
# ~ p0 = {'lam':0.8,'amp':0.07,'base':0}

# SLR version - str exp
# ~ data = bd.bdata(40123,2018)
# ~ pexp = pulsed_strexp(lifetime=bd.life.Li8,pulse_len=data.get_pulse_s())
# ~ fn = lambda time,lam,amp,beta,base : pexp(time,lam,beta,amp) + base
# ~ p0 = {'lam':0.8,'amp':0.07,'base':0,'beta':0.5}

# SLR version - str exp - no baseline
# ~ data = bd.bdata(40123,2018)
# ~ pexp = pulsed_strexp(lifetime=bd.life.Li8,pulse_len=data.get_pulse_s())
# ~ fn = lambda time,lam,amp,beta : pexp(time,lam,beta,amp)
# ~ p0 = {'lam':0.8,'amp':0.07,'beta':0.5}

# draw
# ~ x,y,dy = data.asym('c',rebin=10)
# ~ plt.errorbar(x,y,dy,fmt='.')

# make placer
# ~ f = FunctionPlacer(fig,data,fn,p0)

