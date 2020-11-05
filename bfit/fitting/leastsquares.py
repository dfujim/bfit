# Least squares class for minuit minimizer
# Derek Fujimoto
# Oct 2020

from scipy.misc import derivative 
import numpy as np


class LeastSquares:

    def __init__(self, fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None):
        self.fn = fn
        self.x = x
        self.y = y
        self.n = len(x)
        
        # set errors
        has_dy = False
        if dy is not None:
            has_dy = True
            self.dy = dy
        
        has_dx = False    
        if dx is not None:
            has_dx = True
            self.dx = dx
        
        # asymmetric errors
        has_dy_asym = False
        if dy_low is not None:
            
            if dy is None:
                has_dy = True
                self.dy = dy_low
            else:
                has_dy_asym = True
                self.dy_low = dy_low
        
        has_dx_asym = False
        if dx_low is not None:
            if dx is None:
                has_dx = True
                self.dx = dx_low
            else:
                has_dx_asym = True
                self.dx_low = dx_low
        
        # set least squares function
        if not any((has_dy, has_dx)):
            self.__call__ = self.ls_no_errors
            
        elif has_dy and not has_dx:
            self.__call__ = self.ls_dy

        elif has_dx and not has_dy:
            self.__call__ = self.ls_dx
            
        elif all((has_dy, has_dx)) and not any((has_dx_asym, has_dy_asym)):
            self.__call__ = self.ls_dxdy
            
        elif has_dy_asym and not has_dx:
            self.__call__ = self.ls_dya
        
        elif has_dx_asym and not has_dy:
            self.__call__ = self.ls_dxa
        
        elif all((has_dy_asym, has_dx)) and not has_dx_asym:
            self.__call__ = self.ls_dx_dya
            
        elif all((has_dx_asym, has_dy)) and not has_dy_asym:
            self.__call__ = self.ls_dxa_dy
        
        elif has_dx_asym and has_dy_asym:
            self.__call__ = self.ls_dxa_dya
        
        else:
            raise RuntimeError("Missing case of error assignment")
     
    def __call__(self, pars):
        return self.__call__(*pars)
        
    def ls_no_errors(self, *pars):
        return np.sum(np.square(self.y - self.fn(self.x, *pars)))
            
    def ls_dy(self, *pars):
        return np.sum(np.square((self.y -self.fn(self.x,*pars)) / self.dy))
    
    def ls_dx(self, *pars):
        fprime = derivative(func=self.fn, x0=self.x, dx=1e-6, n=1, order=3, args=pars)
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(self.dx*fprime)
        
        return np.sum(num/den)        

    def ls_dxdy(self, *pars):
        fprime = derivative(func=self.fn, x0=self.x, dx=1e-6, n=1, order=3, args=pars)
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(self.dx*fprime) + np.square(self.dy)
        return np.sum(num/den)   
             
    def ls_dya(self, *pars):
        
        # get errors on appropriate side of the function
        idx = self.y < self.fn(self.x, *pars)
        dy = np.array(self.dy)
        dy[idx] = self.dy_low[idx]
        
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(dy)
        return np.sum(num/den)        
  
    def ls_dxa(self, *pars):
        fprime = derivative(func=self.fn, x0=self.x, dx=1e-6, n=1, order=3, args=pars)
        
        dx = 0.5*(self.dx+self.dx_low)
        
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(dx*fprime)
        return np.sum(num/den)        
       
    def ls_dx_dya(self, *pars):
        fprime = derivative(func=self.fn, x0=self.x, dx=1e-6, n=1, order=3, args=pars)
        
        # get errors on appropriate side of the function
        idx = self.y < self.fn(self.x, *pars)
        dy = np.array(self.dy)
        dy[idx] = self.dy_low[idx]
        
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(dx*fprime) + np.square(dy)
        return np.sum(num/den)    
        
    def ls_dxa_dy(self, *pars):
        fprime = derivative(func=self.fn, x0=self.x, dx=1e-6, n=1, order=3, args=pars)
        
        dx = 0.5*(self.dx+self.dx_low)
        
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(dx*fprime) + np.square(self.dy)
        return np.sum(num/den)    
        
    def ls_dxa_dya(self, *pars):
        fprime = derivative(func=self.fn, x0=self.x, dx=1e-6, n=1, order=3, args=pars)
        
        dx = 0.5*(self.dx+self.dx_low)
        
        # get errors on appropriate side of the function
        idx = self.y < self.fn(self.x, *pars)
        dy = np.array(self.dy)
        dy[idx] = self.dy_low[idx]
        
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(dx*fprime) + np.square(dy)
        return np.sum(num/den)    
        
