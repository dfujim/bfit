# Function constrained by user-defined function
# Derek Fujimoto
# August 2019

import numpy as np

# =========================================================================== # 
class ConstrainedFunction(object):
    """
        bfit
        p1
        p2
        constraints
        defined
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
                'T'     : 'Temperature (K)',
                'TIME'  : 'Start Time',
                'YEAR'  : 'Year',
              }    
                       
    # ======================================================================= # 
    def __init__(self,bfit,constraints,p1,p2):
        """
            constraints:    list of strings corresponding to equations 
                            each of the LHS _MUST_ be one of the p1 values
            p1:             ordered list of strings for the original parameters
            p2:             ordered list of strings for the new parameters
        """

        self.bfit = bfit
        self.p1 = p1
        self.p2 = p2
        self.constraints = constraints
        
        # get list of parameters set by the constraints
        self.defined = [c.split('=')[0] for c in constraints]
        
        # find new parameter names in the string, replace with indexed par
        for i,c in enumerate(self.constraints):
            for j,p in enumerate(self.p2):
                if p in c:
                    c = c.replace(p,'par[%d]'%j)
            self.constraints[i] = c
        
    # ======================================================================= # 
    def __call__(self,data,fn):
        """
            Identify variable names, make constraining function
            
            data: bfitdata object to generate the constrained function 
            fn: function handle
        """
        
        # get variables in decreasing order of length (no mistakes in replace)
        varlist = np.array(list(self.keyvars.keys()))
        varlist = varlist[np.argsort(list(map(len,varlist))[::-1])]
    
        constr = []
        for c in self.constraints:
                
            # find constant names in the string, replace with constant
            for var in varlist:
                if var in c:
                    value = self._get_value(data,var)
                    c = c.replace(var,str(value))
            constr.append(c)
        
        
        
        # get constraint functions, sorted THIS NEEDS FIXING
        header = 'lambda x,%s : ' % (','.join(self.p2))
        constr_fns = []
        for i,p in enumerate(self.p1):
            if p in self.defined:
                j = self.defined.index(p)
                constr_fns.append(eval(header+constr[j].split('=')[1]))
            else:
                constr_fns.append(eval(header+p)
    
        # define the new fitting function
        def new_fn(x,*p2):
            p1 = [c(x,*p2) for c in constr_fns]
            return fn(x,*p1)
            
        return new_fn
            
    # ======================================================================= # 
    def _get_value(self,data,name):
        """
            Tranlate typed constant to numerical value
        """
        
        if   name == 'B0'   :   return data.field.mean
        elif name =='BIAS'  :   return data.bias.mean
        elif name =='CLFT'  :   return data.bd.camp.clift_read.mean
        elif name =='DUR'   :   return data.bd.duration.mean
        elif name =='ENRG'  :   return data.bd.beam_kev()
        elif name =='LAS'   :   return data.bd.epics.las_pwr.mean
        elif name =='NBMR'  :   
            return np.sum([data.hist['NBM'+h].data \
                            for h in ('F+','F-','B-','B+')])/data.duration.mean
        elif name =='RATE'  :   
            hist = ('F+','F-','B-','B+') if data[runs[0]].area == 'BNMR' \
                                         else ('L+','L-','R-','R+')    
            return np.sum([data.hist[h].data for h in hist])/data.duration
        elif name =='RF'    :   return data.bd.camp.rf_dac.mean
        elif name =='RUN'   :   return data.run
        elif name =='T'     :   return data.temperature.mean
        elif name =='TIME'  :   return data.bd.start_time
        elif name =='YEAR'  :   return data.year
