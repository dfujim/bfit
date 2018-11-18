# Fit set of data globally 
# Derek Fujimoto
# Nov 2018

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os, collections

__doc__=\
"""
    Global fitter. 
    
    Uses scipy.optimize.curve_fit to fit a function or list of functions to a 
    set of data with shared parameters.
    
    Usage: 
        
        Construct fitter:
            
            g = global_fitter(x,y,dy,fn,sharelist,npar=-1)
            
            %s
    
        Fit
            g.fit(**fitargs)
        
            %s
            
        Get chi squared
            g.get_chi()
            
            %s
        
        Get fit parameters
            g.get_par()
            
            %s
            
        Draw the result
        
            g.draw(mode='stack',xlabel='',ylabel='',do_legend=False,labels=None,
                   savefig='',**errorbar_args)
           
            %s
"""


# =========================================================================== #
class global_fitter(object):
    """
        Set up fitting a set of data with arbitrary function. Arbitrary 
        globally shared parameters. 
        
        Instance Variables: 
            
            chi_glbl                global chisqured
            chi                     list of chisquared values for each data set
            
            fn                      list of fitting function handles
            fitfn                   handle for fitting function on ccat data
            
            npar                    number of parameters in input function
            nsets                   number of data sets
            par_index               index of parameters to do sharing
            
            par                     fit results with unnecessary variables stripped
            std                     fit errors with unnecessary variables stripped
            cov                     fit covarince matrix with unnecessary variables stripped
            
            sharelist               array of bool of len = nparameters, share parameter if true. 
            
            xccat                   concatenated xdata for global fitting
            yccat                   concatenated ydata for global fitting
            dyccat                  concatenated dydata for global fitting
            
            xdata                   input array of x data sets [array1,array2,...]
            ydata                   input array of y data sets [array1,array2,...]
            dydata                  input array of y error sets [array1,array2,...]
    """
    
    # class variables
    x_split = 1                 # time to add between run (arb.)
    draw_modes = ['stack','s','new','n','append','a']   # for checking modes
    ndraw_pts = 500             # number of points to draw fits with
    
    # ======================================================================= #
    def __init__(self,x,y,dy,fn,sharelist,npar=-1):
        """
            x,y:        2-list of data sets of equal length. 
                        fmt: [[a1,a2,...],[b1,b2,...],...]
            
            dy:         list of errors in y with same format as y
            
            fn:         function handle OR list of function handles. 
                        MUST specify inputs explicitly
                        if list must have that len(fn) = len(x)
            
            sharelist:  tuple of booleans indicating which values to share. 
                        len = number of parameters 
                        
            npar:       number of free parameters in each fitting function.
                        Set if number of parameters is not intuitable from 
                            function code.
        """
        
        # save inputs
        self.xdata = np.asarray(x)
        self.ydata = np.asarray(y)
        self.dydata = np.asarray(dy)
        self.fn = fn
        self.sharelist = sharelist
        
        # check in input function is iterable
        if not isinstance(self.fn,collections.Iterable):
            self.fn = [self.fn for i in range(self.nsets)]
        
        # get number of parameters
        if npar < 0:
            self.npar = len(self.fn[0].__code__.co_varnames)-1
        else:
            self.npar = npar
        
        # get number of data sets
        self.nsets = len(self.xdata)
        
        # check that input data is of the right format
        self._check_input_data()
        
        # get data for appended runs
        self.xccat,self.yccat,self.dyccat = self._get_data()
        
        # set index
        self.par_index = self._get_shared_index()
        
        # get fit function
        self.fitfn = self._get_fitfn()
        
    # ======================================================================= #
    def draw(self,mode='stack',xlabel='',ylabel='',do_legend=False,labels=None,
             savefig='',**errorbar_args):
        """
            Draw data and fit results. 
            
            mode:           drawing mode. 
                            one of 'stack', 'new', 'append' (or first character 
                                for shorhand)
            
            xlabel/ylabel:  string for axis labels
            
            do_legend:      if true set legend
            
            labels:         list of string to label data
            
            savefig:        if not '', save figure with this name
            
            errorbar_args:  arguments to pass on to plt.errorbar
            
            Returns list of matplotlib figure objects
        """
        
        fig_list = []
        last = 0
        
        # check input
        if mode not in self.draw_modes:
            raise RuntimeError('Drawing mode %s not recognized' % mode)
        
        # get label
        if type(labels) == type(None):
            labels = ['_no_label_' for i in range(self.nsets)]
        
        # get fit parameters
        par_index = self.par_index.reshape(-1,self.npar)
        
        # draw all
        for i in range(self.nsets):
            
            # get data
            x,y,dy = self.xdata[i], self.ydata[i], self.dydata[i]
            f = self.fn[i]
            
            # make new figure
            if mode in ['new','n']:            
                fig_list.append(plt.figure())
            elif len(fig_list) == 0:
                fig_list.append(plt.figure())
            
            # shift x values
            if mode in ['append','a']:
                x_draw = x+last+self.x_split
                last = x_draw[-1]
            else:
                x_draw = x
                
            # draw data
            datplt = plt.errorbar(x_draw,y,dy,label=labels[i],**errorbar_args)
            
            # get color for fit curve
            if mode in ['stack','s','append','a']:
                color = datplt[0].get_color()
            else:
                color = 'k'
            
            # draw fit
            xfit = np.arange(self.ndraw_pts)/self.ndraw_pts*(max(x)-min(x))+min(x)
            xdraw = np.arange(self.ndraw_pts)/self.ndraw_pts*(max(x_draw)-min(x_draw))+min(x_draw)
            plt.plot(xdraw,f(xfit,*self.par[par_index[i]]),color=color,zorder=10)
        
            # plot elements
            plt.ylabel(ylabel)
            plt.xlabel(xlabel)
            
            if do_legend:       plt.legend(fontsize='x-small')
            if savefig!='':     plt.savefig(savefig)
            
            plt.tight_layout()

        return fig_list
        
    # ======================================================================= #
    def fit(self,**fitargs):
        """
            fitargs: parameters to pass to fitter (scipy.optimize.curve_fit) 
            
            p0:         [(p1,p2,...),...] innermost tuple is initial parameters 
                            for each data set, list of tuples for all data sets
                            if not enough sets of inputs, last input is copied 
                            for remaining data sets.
                            
                            p0.shape = (nsets,npars)
                    OR
                        (p1,p2,...) single tuple to set same initial parameters 
                            for all data sets
            
                            p0.shape = (npars,)
            
            bounds:     [((l1,l2,...),(h1,h2,...)),...] similar to p0, but use 
                            2-tuples instead of the 1-tuples of p0
                        
                            bounds.shape = (nsets,2,npars)
                        
                    OR
                        ((l1,l2,...),(h1,h2,...)) single 2-tuple to set same 
                            bounds for all data sets
                            
                            bounds.shape = (2,npars)
                            
                            
            returns (parameters,stdev)
        """
        # get rid of zero errors
        tag = self.dyccat != 0
        
        # set default p0
        if 'p0' not in fitargs:
            p0 = np.ones((self.nsets,self.npar))
        else:
            p0 = np.asarray(fitargs['p0'])
            
        # build and flatten p0
        sh = p0.shape
        if len(sh) == 1:    # one input
            p0 = np.concatenate([p0 for i in range(self.nsets)])
        else:               # list input
            p0_add = [p0[-1] for i in range(self.nsets-sh[0])]
            p0 = np.concatenate((*p0,*p0_add))
        
        # reshuffle input p0 to have no excess inputs
        uniq = np.unique(self.par_index)
        p0_new = [p0[i] for i in uniq]
        fitargs['p0'] = np.array(p0_new)
        
        # do bounds input
        try:
            bounds = np.asarray(fitargs['bounds'])
        except KeyError:
            pass
        else:
            # build and flatten bounds
            sh = bounds.shape
            if len(sh) == 2:    # one input
                lo = np.concatenate([bounds[0] for i in range(self.nsets)])
                hi = np.concatenate([bounds[1] for i in range(self.nsets)])
            else:               # list input
                lo_add = [bounds[-1][0] for i in range(self.nsets-sh[0])]
                hi_add = [bounds[-1][1] for i in range(self.nsets-sh[0])]
                lo = np.concatenate((*bounds[:,0,:],*lo_add))
                hi = np.concatenate((*bounds[:,1,:],*hi_add))
        
            bounds = np.array((lo,hi))
            
            # reshuffle bounds
            lo = lo[uniq]
            hi = hi[uniq]
            fitargs['bounds'] = np.array((lo,hi))
        
        # do fit
        par,cov = curve_fit(self.fitfn,
                            self.xccat[tag],
                            self.yccat[tag],
                            sigma=self.dyccat[tag],
                            **fitargs)
        # to array
        par = np.asarray(par)
        cov = np.asarray(cov)
        std = np.sqrt(np.diag(cov))
        
        # expand parameters
        par_out = par[self.par_index].reshape(-1,self.npar)
        std_out = std[self.par_index].reshape(-1,self.npar)
        
        # return
        self.par = par
        self.std = std
        self.cov = cov
        return (par_out,std_out)
    
    # ======================================================================= #
    def get_chi(self):
        """
            Calculate chisq/DOF, both globally and for each function.
            
            sets self.chi and self.chi_glbl
            
            return (global chi, list of chi for each fn)
        """
        
        # global
        tag = self.dyccat != 0
        
        dof = len(self.xccat[tag])-(self.npar*self.nsets)
        self.chi_glbl = np.sum(np.square((self.yccat[tag]-\
                      self.fitfn(self.xccat[tag],*self.par))/self.dyccat[tag]))/dof
        
        # get fit parameters, with sharing
        par_index = self.par_index.reshape(-1,self.npar)
        pars = (self.par[p] for p in par_index)
        
        # single fn chisq
        self.chi = []
        for x,y,dy,p,f in zip(self.xdata,self.ydata,self.dydata,pars,self.fn):
            tag = dy != 0
            dof = len(x[tag])-(self.npar)
            self.chi.append(\
                    np.sum(np.square((y[tag]-f(x[tag],*p))/dy[tag]))/dof)
        
        return (self.chi_glbl,self.chi)

    # ======================================================================= #
    def get_par(self):
        """
            Fetch fit parameters as dictionary
            
            return 2-tuple of (par,error) each with format
            
            [data1:[par1,par2,...],data2:[],...]
        """
    
        par = self.par[self.par_index].reshape(-1,self.npar)
        std = self.std[self.par_index].reshape(-1,self.npar)
        
        return (par,std)
    
    # ======================================================================= #
    def _check_input_data(self):
        """Check input data lengths match. Raise exception on failure."""
        
        # test number of data sets
        if not len(self.xdata) == len(self.ydata) == len(self.dydata):
            raise RuntimeError('Lengths of input data arrays do not match.\n'+\
                'nsets: x, y, dy =  %d, %d, %d\n' % (len(self.xdata),
                                                     len(self.ydata),
                                                     len(self.dydata)))            
        
        # TEST SHARED INPUT ===================================================
        if len(self.sharelist) > self.npar:
            raise RuntimeError('Length of sharelist is too large. '+\
                       'len(sharelist) [%d] == len(fn parameters [%d])'%\
                        (len(self.sharelist),self.npar))
    
    # ======================================================================= #
    def _get_data(self):
        """
            Get list of concatenated data
            
            return (x,y,dy)
        """
        
        # space out x data 
        xdata = np.copy(self.xdata)
        for i in range(1,len(xdata)):
            xdata[i] += xdata[i-1][-1]+self.x_split
        
        # concatenate
        x = np.concatenate(xdata)
        y = np.concatenate(self.ydata)
        dy =np.concatenate(self.dydata)

        return (x,y,dy)

    # ======================================================================= #
    def _get_fitfn(self):
        """
            Get fitfn for appended data
            return fit function handle
        """
        
        # set parameter indexes with sharing
        par_index = self.par_index.reshape(-1,self.npar)
        
        # get data without zeros
        xdata = np.array([x[dy!=0] for x,dy in zip(self.xdata,self.dydata)])
        
        # make fit function: assign parameters  
        def fitfn(unused,*par):
            return np.concatenate([f(x,*(np.asarray(par)[p])) \
                                    for x,p,f in zip(xdata,par_index,self.fn)])
        return fitfn

    # ======================================================================= #
    def _get_shared_index(self):
        """
            Indexes of parameters in parameter input list, with sharing
            
            return list of indexes to access parameters.
        """
        
        npar = self.npar
        nsets = self.nsets
        
        # set parameter indexes with sharing
        par_index = np.arange(npar*nsets)
        par_shared = np.zeros(len(par_index))
        
        # set indexes for sharing.
        add = np.arange(npar,npar*nsets,npar)   # offsets to set all other pars
        for i,s in enumerate(self.sharelist):
            # parameter is shared
            if s:
                
                # get positions of shared parameters
                addi = add+i
                
                # equate shared parameters, tag
                par_index[addi] = par_index[i] 
                par_shared[addi] = 1
                
                # shift indexes of intermediate parameters
                offset = 1
                for j in range(addi[0]+1,len(par_index)):
                    if j in addi: 
                        offset += 1
                    elif not par_shared[j]:
                        par_index[j] -= offset
                    
        return par_index


# Add to module docstring
__doc__ = __doc__ % (global_fitter.__init__.__doc__,
                     global_fitter.fit.__doc__,
                     global_fitter.get_chi.__doc__,
                     global_fitter.get_par.__doc__,
                     global_fitter.draw.__doc__,
                     )
