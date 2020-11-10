# Function for calculating new user-defined parameters
# Derek Fujimoto
# Nov 2020

import numpy as np
from bfit.backend.ConstrainedFunction import ConstrainedFunction

# =========================================================================== # 
class ParameterFunction(ConstrainedFunction):
    """
        name:           name of the parameter being defined
        inputs:         list of strings for parameter inputs to equation
        equation:       function handle, the equation defining the parameter
    """
    
    # ======================================================================= # 
    def __init__(self, name, equation, parnames, bfit):
        """
            bfit:           pointer to bfit object
            name:           name of parameter which we are defining (LHS)
            equation:       string corresponding to equation RHS
            parnames:       list of strings for fit parameter names
        """
        self.bfit = bfit
        
        # equations and names
        self.name = name
        
        # get variables in decreasing order of length (no mistakes in replace)
        varlist = np.array(list(self.keyvars.keys()))
        varlist = varlist[np.argsort(list(map(len,varlist))[::-1])]
    
        # replace 1_T1 with lambda
        while '1_T1' in equation:
            equation = equation.replace('1_T1', 'lambda1')
        
        self.parnames = list(parnames)
        for i,p in enumerate(self.parnames):
            while '1_T1' in p:
                p = p.replace('1_T1', 'lambda1')
            self.parnames[i] = p
    
        # make list of input names from meta data
        self.inputs = []
        
        for var in varlist:
            if var in equation:
                self.inputs.append(var)
                
        # make list of input names from parameter names
        for var in self.parnames:
            if var in equation:
                self.inputs.append(var)
                
        # make equation
        input_str = ', '.join(self.inputs)
        self.equation = eval('lambda %s : %s' % (input_str, equation))
        
        # add name to draw_components
        draw_comp = self.bfit.fit_files.draw_components
        if name in draw_comp:
            draw_comp.remove(name)
        draw_comp.append(name)
        
    # ======================================================================= # 
    def __call__(self):
        """ 
            Get data and calculate the parameter
        """
        
        inputs = {}
        runs = sorted(self.bfit.data.keys())
        for var in self.inputs:
            
            # get value for all data
            if var in self.keyvars:
                values = [self._get_value(self.bfit.data[r], var) for r in runs]
            elif var in self.parnames:
                
                var_par = var.replace('lambda1','1_T1')
                values = [self.bfit.data[r].fitpar['res'][var_par] for r in runs]
                    
            # set up inputs
            inputs[var] = np.array(values)
                            
        # calculate the parameter
        return self.equation(**inputs)
        
