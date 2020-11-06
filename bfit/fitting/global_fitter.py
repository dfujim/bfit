# Fit set of data globally 
# Derek Fujimoto
# Nov 2018

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os, collections
import time

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
            fixed                   list of fixed variables (corresponds to input)
            
            metadata                array of additional inputs, fixed for each data set
                                    (if len(shared) < len(actual inputs))
            
            minimizer               string: one of "curve_fit" or "migrad"
            
            npar                    number of parameters in input function
            nsets                   number of data sets
            
            par                     fit results with unnecessary variables stripped 
            par_runwise             fit results run-by-run with all needed inputs
            cov                     fit covarince matrix with unnecessary variables stripped
            cov_runwise             fit covarince matrix run-by-run with all needed inputs
            
            shared                  array of bool of len = nparameters, share parameter if true. 
            sharing_links           2D array of ints, linking global inputs to function-wise inputs
            
            xcat                    concatenated xdata for global fitting
            ycat                    concatenated ydata for global fitting
            dycat                   concatenated dydata for global fitting
            dxcat                   concatenated dydata for global fitting
            dycat_low               concatenated dydata for global fitting
            dxcat_low               concatenated dydata for global fitting
            
            x                       input array of x data sets [array1,array2,...]
            y                       input array of y data sets [array1,array2,...]
            dy                      input array of y error sets [array1,array2,...]
            dx                      input array of x error sets [array1,array2,...]
            dy_low                  input array of y error sets [array1,array2,...]
            dx_low                  input array of x error sets [array1,array2,...]
    """
    
    # class variables
    draw_modes = ('stack','s','new','n','append','a')   # for checking modes
    ndraw_pts = 500             # number of points to draw fits with
    
    # ======================================================================= #
    def __init__(self, fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, 
                shared=None, fixed=None, metadata=None, minimizer='migrad'):
        """
            fn:         function handle OR list of function handles. 
                        MUST specify inputs explicitly if list must have that 
                        len(fn) = len(x) and all function must have the same 
                        inputs in the same order
        
            x, y:       2-list of data sets of equal length. 
                        fmt: [[a1,a2,...],[b1,b2,...],...]
            
            dx, dy:     list of errors in x or y with same format as x and y
            dx_low, dy_low: list of low bound errors in x or y with same format 
                        as x and y. 
                            
                        If not None, then assume dy and dx are the upper errors
                        If None, assume symmetric errors
            
            shared:     tuple of booleans indicating which values to share. 
                        len = number of parameters 
                        
            fixed:      list of booleans indicating if the paramter is to be 
                        fixed to p0 value (same length as p0). Returns best 
                        parameters in order presented, with the fixed 
                        parameters omitted.
                        
            metadata:   array of values to pass to fn which are fixed for each 
                        data set (ex: the temperature of each data set). 
                        format: len(metadata) = number of data sets. 
                        
                        number of parameters is set by len(shared), all 
                        remaining inputs are expected to be metadata inputs
                        function call: fn[i](x[i],*par[i],*metadata[i])
                        
            minimizer:  string. One of "curve_fit" or "migrad" indicating which 
                        code to use to minimize the function
        """
        # ---------------------------------------------------------------------
        # Check and assign inputs
        
        # check error input
        if (dy is None and dy_low is not None) or (dx is None and dx_low is not None): 
            raise RuntimeError("If specifying lower errors, must also specify dy or dx")
            
        # data types
        x = list(x)
        y = list(y)
        
        self.nsets = len(x)
        if dy is not None:      dy = list(dy)
        else:                   dy = np.full(self.nsets, None)
        
        if dx is not None:      dx = list(dx)
        else:                   dx = np.full(self.nsets, None)
        
        if dy_low is not None:      dy_low = list(dy_low)
        else:                       dy_low = np.full(self.nsets, None)
        
        if dx_low is not None:      dx_low = list(dx_low)
        else:                       dx_low = np.full(self.nsets, None)
        
        self.minimizer = minimizer
        
        # shared parameters
        self.shared = np.asarray(shared)
        
        # get number of input parameters
        if shared is None:
            raise RuntimeError("Must specified shared parameter as boolean iterable")
        self.npar = len(shared)
        
        # test number of data sets
        msg = 'Lengths of input data arrays do not match.\nnsets: %s, %s =  %d, %d\n'
        if not len(x) == len(y):
            raise RuntimeError(msg % ('x', 'y', len(x), len(y)))
        
        if not self.nsets == len(dy):
            raise RuntimeError(msg % ('n', 'dy', self.nsets, len(dy)))
        if not self.nsets == len(dx):
            raise RuntimeError(msg % ('n', 'dx', self.nsets, len(dx)))
        if not self.nsets == len(dy_low):
            raise RuntimeError(msg % ('n', 'dy_low', self.nsets, len(dy_low)))
        if not self.nsets == len(dx_low):
            raise RuntimeError(msg % ('n', 'dx_low', self.nsets, len(dx_low)))
        
        # if errors, remove points with zero error from data
        for i in range(self.nsets):
            
            # get indexing
            idx = np.full(len(x[i]), False)
            if dy[i] is not None:      idx += dy[i] != 0
            if dx[i] is not None:      idx += dx[i] != 0
            if dy_low[i] is not None:  idx += dy_low[i] != 0
            if dx_low[i] is not None:  idx += dx_low[i] != 0
            
            # crop
            x[i] = x[i][idx]
            y[i] = y[i][idx]
            
            if dy[i] is not None:      dy[i] = dy[i][idx]
            if dx[i] is not None:      dx[i] = dx[i][idx]
            if dy_low[i] is not None:  dy_low[i] = dy_low[i][idx]
            if dx_low[i] is not None:  dx_low[i] = dx_low[i][idx]
        
        # check if list of functions given 
        if not isinstance(fn,collections.Iterable):
            fn = [fn]*self.nsets
        
        # check metadata
        if metadata is not None:
            
            # check for not enough data
            if len(metadata) != self.nsets:
                raise RuntimeError('metadata has the wrong shape: len(metadata) = len(x)')  
                
            # check for 1D input
            metadata = np.asarray(metadata)
            if len(metadata.shape) == 1:
                metadata = np.asarray([metadata]).T
        else:
            metadata = [[]]*self.nsets
        self.metadata = metadata
        
        # expand fixed
        if fixed is not None: 
            if len(np.asarray(fixed).shape) == 1:
                fixed = np.full((self.nsets,self.npar),fixed)
            else:
                fixed = np.asarray(fixed)
        else:
            fixed = np.zeros((self.nsets,self.npar)).astype(bool)
        
        fixed_flat = np.concatenate(fixed)
        
        # check that no shared parameters are fixed
        shared_as_int = self.shared.astype(int)
        for fix in fixed: 
            if any(fix+shared_as_int>1):
                raise RuntimeError('Cannot fix a shared parameter') 
        
        # ---------------------------------------------------------------------
        # Build fitting functions
        
        # get linking indexes    
        sharing_links = [] # [input index] organized by output index position
        p_index = 0
        par_numbers_shared = np.arange(self.npar)
        
        for i in range(self.nsets):
            
            # parameter intdexes
            par_numbers = par_numbers_shared+p_index
            
            # link shared variables
            par_numbers[self.shared] = par_numbers_shared[self.shared]  
            
            # link fixed variables
            par_numbers[fixed[i]] = -par_numbers[fixed[i]]-1
            sharing_links.append(par_numbers)
            
            # iterate
            p_index += self.npar
        
        # reduce too-high indexes
        sharing_links = np.array(sharing_links)        
        unq = np.unique(sharing_links)
        unq = unq[unq>=0]
        for i,u in enumerate(unq):
            sharing_links[sharing_links==u] = i
        
        # save results
        self.fn = fn
        self.x = x
        self.y = y
        self.dy = dy
        self.dx = dx
        self.dy_low = dy_low
        self.dx_low = dx_low
        self.fixed = fixed
        self.sharing_links = sharing_links
        
        # get concatenated data
        self.xcat = np.concatenate(x)
        self.ycat = np.concatenate(y)
        
        if dy[0] is not None:       self.dycat = np.concatenate(dy)
        else:                       self.dycat = dy
        
        if dx[0] is not None:       self.dxcat = np.concatenate(dx)
        else:                       self.dxcat = dx
        
        if dy_low[0] is not None:   self.dycat_low = np.concatenate(dy)
        else:                       self.dycat_low = dy
        
        if dx_low[0] is not None:   self.dxcat_low = np.concatenate(dx)
        else:                       self.dxcat_low = dx
        
    # ======================================================================= #
    def _do_curve_fit(self, master_fn, p0_first, **fitargs):
        
        par,cov = curve_fit(master_fn,
                            self.xcat,
                            self.ycat,
                            sigma=self.dycat,
                            absolute_sigma=True,
                            p0 = p0_first,
                            **fitargs)
                            
        std = np.diag(cov)**0.5
        return (par, std, std, cov)
        
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
        if labels is None:
            labels = ['_no_label_' for i in range(self.nsets)]
        
        # draw all
        for i in range(self.nsets):
            
            # get data
            x, y, = self.x[i], self.y[i]
            dy, dx = self.dy[i], self.dx[i]
            dy_low, dx_low = self.dy_low[i], self.dx_low[i]
            f = self.fn[i]
            md = self.metadata[i]
            
            if dy_low is None: dy_low = dy
            if dx_low is None: dx_low = dx
            
            # make new figure
            if mode in ['new','n']:            
                fig_list.append(plt.figure())
            elif len(fig_list) == 0:
                fig_list.append(plt.figure())
            
            # shift x values
            if mode in ['append','a']:
                x_draw = x+last
                last = x_draw[-1]
            else:
                x_draw = x
                
            # draw data
            if dy is None:      dy_draw = None
            else:               dy_draw = (dy_low, dy)    
            if dx is None:      dx_draw = None
            else:               dx_draw = (dx_low, dx)    
            datplt = plt.errorbar(x_draw, y, yerr=dy_draw, xerr=dx_draw, 
                                  label=labels[i], **errorbar_args)
            
            # get color for fit curve
            if mode in ['stack','s']:
                color = datplt[0].get_color()
            else:
                color = 'k'
            
            # draw fit
            xfit = np.linspace(min(x), max(x), self.ndraw_pts)
            xdraw = np.linspace(min(x_draw), max(x_draw), self.ndraw_pts)
            plt.plot(xdraw,f(xfit, *self.par_runwise[i], *md), color=color, zorder=10)
        
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
                            
                            
            returns (parameters,covariance matrix)
        """
        
        # get values from self
        fixed = self.fixed
        shared = self.shared
        sharing_links = self.sharing_links
        fn = self.fn
        
        # set default p0
        if 'p0' in fitargs:
            p0 = np.asarray(fitargs['p0'])
            del fitargs['p0']
            
            # expand p0
            if len(p0.shape) == 1:
                p0 = np.full((self.nsets, self.npar), p0)
                
        else:
            p0 = np.ones((self.nsets, self.npar))
        
        # for fixed parameters
        p0_flat_inv = np.concatenate(p0)[::-1]
        
        # get flattened p0 values which are not fixed
        p0_first = self._flatten(p0)
        
        # set default bounds
        try:
            bounds = np.asarray(fitargs['bounds'])
        except KeyError:
            bounds = None
        else:
            
            # treat low and high bounds seperately 
            if len(bounds.shape) > 2:
                lo = bounds[:,0,:]
                hi = bounds[:,1,:]
            else:
                lo = np.asarray(bounds[0])
                hi = np.asarray(bounds[1])
            
            # expand bounds
            lo = self._expand_bound_lim(lo)
            hi = self._expand_bound_lim(hi)
            
            # flatten bounds 
            lo = self._flatten(lo)
            hi = self._flatten(hi)
            
            # construct bounds
            bounds = (lo,hi)
            fitargs['bounds'] = bounds
        
        # make the master function 
        x = self.x
        rng = range(self.nsets)
        metadata = self.metadata
        def master_fn(x_unused,*par):            
            inputs = np.take(np.hstack((par, p0_flat_inv)), sharing_links)
            return np.concatenate([fn[i](x[i], *inputs[i], *metadata[i]) for i in rng])
        
        self.master_fn = master_fn
          
        # do fit
        if self.minimizer == 'curve_fit':
            par, std_l, std_u, cov = self._do_curve_fit(master_fn, p0_first, **fitargs)
        elif self.minimizer == 'migrad':
            par, std_l, std_u, cov = self._do_migrad(master_fn, p0_first, **fitargs)
        else:
            raise RuntimeError("Bad minimizer input")
        
        # to array
        par = np.asarray(par)
        std_l = np.asarray(std_l)
        std_u = np.asarray(std_u)
        cov = np.asarray(cov)
        
        
        # inflate parameters
        par_out = np.hstack((par,p0_flat_inv))[sharing_links]
        
        zero = np.zeros(len(p0_flat_inv))
        std_l_out = np.hstack((std_l, zero))[sharing_links]
        std_u_out = np.hstack((std_u, zero))[sharing_links]
        
        # inflate covariance matrix
        cov_out = []
        for lnk in sharing_links:
            
            # init
            cov_run = np.zeros((self.npar, self.npar))
            
            # assign
            for i in range(self.npar):
                for j in range(self.npar):
                    
                    # fixed values
                    if lnk[j] < 0 or lnk[i] < 0: 
                        cov_run[i,j] = np.nan
                    
                    # cov
                    else:
                        cov_run[i,j] = cov[lnk[i],lnk[j]]
            cov_out.append(cov_run)
                    
        # return
        self.par = par
        self.cov = cov
        self.par_runwise = par_out
        self.cov_runwise = cov_out
        
        return (par_out, cov_out)
    
    # ======================================================================= #
    def get_chi(self):
        """
            Calculate chisq/DOF, both globally and for each function.
            
            sets self.chi and self.chi_glbl
            
            return (global chi, list of chi for each fn)
        """

        # global
        dof = len(self.xcat)-len(self.par)
        self.chi_glbl = np.sum(np.square((self.ycat-\
                      self.master_fn(self.xcat,*self.par))/self.dycat))/dof
            
        # single fn chisq
        self.chi = []
        for x, y, dy, p, f, fx, m in zip(self.x, self.y, self.dy, 
                                        self.par_runwise, self.fn, self.fixed, 
                                        self.metadata):
            dof = len(x)-self.npar+sum(fx)
            self.chi.append(np.sum(np.square((y-f(x, *p, *m))/dy))/dof)
        
        return (self.chi_glbl, self.chi)

    # ======================================================================= #
    def get_par(self):
        """
            Fetch fit parameters
            
            return 2-tuple of (par,cov) with format
            
            ([data1:[par1,par2,...],data2:[],...],
             [data1:[cov1,cov2,...],data2:[],...])
        """
        cov = self.cov_runwise
        std = np.array(list(map(np.diag,cov)))**0.5
        
        return (self.par_runwise,cov,std)
    
    # ======================================================================= #
    def _expand_bound_lim(self,lim):
        """
            For various bound input formats expand such that all bounds are 
            defined explicitly. 
        """

        lim = np.asarray(lim)
        
        # single float case
        if not lim.shape:
            return np.full((self.nsets,self.npar),np.full(self.npar,lim))
            
        # list case: probably each variable defined
        if len(lim.shape) == 1 and len(lim) == self.npar:
            return np.full((self.nsets,self.npar),lim)
        
        # list case: probably each data set defined in full
        if lim.shape == (self.nsets,self.npar):
            return lim
        
        # we don't know what's happening
        raise RuntimeError('Unexpected bound size input')
        
    # ======================================================================= #
    def _flatten(self,arr):
        """
            Flatten input array based on sharing and fixing. 
            Use for p0,bounds
        """
    
        fixed = self.fixed
        shared = self.shared
    
        arr2 = list(arr[0][~fixed[0]])
        for i in range(1,len(arr)):
            arr2.extend(arr[i][(~fixed[i])*(~shared)])
        return np.array(arr2)
    
# Add to module docstring
__doc__ = __doc__ % (global_fitter.__init__.__doc__,
                     global_fitter.fit.__doc__,
                     global_fitter.get_chi.__doc__,
                     global_fitter.get_par.__doc__,
                     global_fitter.draw.__doc__,
                     )
