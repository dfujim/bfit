# Function constrained by user-defined function
# Derek Fujimoto
# August 2019

import numpy as np

# =========================================================================== # 
class ConstrainedFunction(object):
    """
        p1
        p2
        constraints
        defined
        equation
    """
    
    # keywords used to identify variables
    keyvars = { 'B0'    : 'B0 Field (T)', 
                'BIAS'  : 'Platform Bias (kV)',
                'CLFT'  : 'Cryo Lift Read (mm)',
                'DUR'   : 'Run Duration (s)',
                'ENRG'  : 'Impl. Energy (keV)',
                'LAS'   : 'Laser Power',
                'NBMR'  : 'NBM Rate (count/s)',
                'RATE'  : 'Sample Rate (count/s)',
                'RF'    : 'RF Level DAC',
                'RUN'   : 'Run Number',
                'TEMP'  : 'Temperature (K)',
                'TIME'  : 'Start Time',
                'YEAR'  : 'Year',
              }    
                       
    # ======================================================================= # 
    def __init__(self, defined, equation, newpar, oldpar):
        """
            defined:        parameters which the equations define (equation LHS)
                            in old parameter order
            equation:       list of strings corresponding to equation RHS in old 
                            parameter order
            newpar:         list of strings corresponding to new function 
                            parameters in order
            oldpar:         list of strings corresponding to old function 
                            parameters in order
        """
        self.header = 'lambda %s : ' % (','.join(newpar))
        self.oldpar = oldpar
        
        # sort equations and defined by old par
        self.equation = [equation[defined.index(p)] for p in oldpar]
        
    # ======================================================================= # 
    def __call__(self, data, fn):
        """ 
            Identify variable names, make constraining function
            
            data: bfitdata object to generate the constrained function 
            fn: function handle
        """
        
        # get variables in decreasing order of length (no mistakes in replace)
        varlist = np.array(list(self.keyvars.keys()))
        varlist = varlist[np.argsort(list(map(len,varlist))[::-1])]
    
        eqn = []
        for c in self.equation:
                
            # find constant names in the string, replace with constant
            for var in varlist:
                if var in c:
                    value = self._get_value(data, var)
                    c = c.replace(var, str(value))
            eqn.append(c)
        
        # get constraint functions, sorted 
        constr_fns = [eval(self.header+e)for e in eqn]    
        
        # define the new fitting function
        def new_fn(x,*newparam):
            oldparam = [c(*newparam) for c in constr_fns]
            return fn(x, *oldparam)
            
        return (new_fn, constr_fns)
            
    # ======================================================================= # 
    def _get_value(self, data, name):
        """
            Tranlate typed constant to numerical value
        """
        
        if   name == 'B0'   :   return data.field
        elif name =='BIAS'  :   return data.bias
        elif name =='CLFT'  :   return data.bd.camp.clift_read.mean
        elif name =='DUR'   :   return data.bd.duration
        elif name =='ENRG'  :   return data.bd.beam_kev()
        elif name =='LAS'   :   return data.bd.epics.las_pwr.mean
        elif name =='NBMR'  :   
            return np.sum([data.hist['NBM'+h].data \
                           for h in ('F+','F-','B-','B+')])/data.duration
        elif name =='RATE'  :   
            hist = ('F+','F-','B-','B+') if data.area == 'BNMR' \
                                         else ('L+','L-','R-','R+')    
            return np.sum([data.hist[h].data for h in hist])/data.duration
        elif name =='RF'    :   return data.bd.camp.rf_dac.mean
        elif name =='RUN'   :   return data.run
        elif name =='TEMP'  :   return data.temperature.mean
        elif name =='TIME'  :   return data.bd.start_time
        elif name =='YEAR'  :   return data.year
