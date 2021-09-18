from tkinter import *
from functools import partial
import bfit.backend.colors as colors


class InputLine(object):
    """
        Stores one line of inputs: 
            'p0', 'blo', 'bhi', 'res', 'dres-', 'dres+', 'chi', 'fixed', 'shared'
        as well as the frames and variables        
        
        bfit: bfit object
        entry: dict[col] = entry or checkbutton object
        fitline: fitline object
        frame: ttk.Frame
        label: ttk.label, parameter name
        pname: string, name of parameter for this line
        variable: dict[col] = variable (StringVar or BooleanVar)            
    """
    
    width = 13
    width_chi = 7
    columns = ['p0', 'blo', 'bhi', 'res', 'dres-', 'dres+', 'chi', 'fixed', 'shared']

    # ======================================================================= #
    def __init__(self, frame, bfit, fitline, show_chi=False):
        """
            frame: frame in which line will grid (first row is 1)
            show_chi: if true, grid the chi parameter
        """
        self.pname = ''
        self.bfit = bfit
        self.fitline = fitline
        self.frame = frame
        self.label = ttk.Label(self.frame, text=self.pname, justify='right')
        
        self.variable = {   'p0': StringVar(),
                            'blo': StringVar(),
                            'bhi': StringVar(),
                            'res': StringVar(),
                            'dres-': StringVar(),
                            'dres+': StringVar(),
                            'chi': StringVar(),
                            'fixed': BooleanVar(),
                            'shared': BooleanVar(),                            
                        }
        
        self.entry = {}
        for key, var in self.variable.items():
        
            # stringvar
            if key not in ('fixed', 'shared'):
                
                if key == 'chi':
                    width = self.width_chi
                else:
                    width = self.width
                
                self.entry[key] = Entry(self.frame, 
                                          textvariable=self.variable[key], 
                                          width=width)
        
            # booleanvar
            else:
                self.entry[key] = ttk.Checkbutton(self.frame, 
                                                  text='', 
                                                  variable=self.variable[key], 
                                                  onvalue=True, 
                                                  offvalue=False)
        
            # set colors and state
            if key in ('res', 'dres-', 'dres+', 'chi'):
                self.entry[key]['state'] = 'readonly'
                self.entry[key]['foreground'] = colors.foreground
        
        # disallow fixed and shared variables
        share = self.variable['shared']
        share.trace_id = share.trace("w", self._unfix)
        share.trace_callback = self._unfix
      
        fixed = self.variable['fixed']
        fixed.trace_id = fixed.trace("w", self._unshare)
        fixed.trace_callback = self._unshare
      
        # set modify all synchronization
        for k in ('p0', 'blo', 'bhi', 'fixed'):

            # set new trace callback
            self.variable[k].trace_id = \
                self.variable[k].trace("w", partial(self._sync_values, col=k))
            self.variable[k].trace_callback = partial(self._sync_values, col=k)


    # ======================================================================= #
    def _sync_values(self, *args, col):
        """
            Do modify all synchronization. Make other lines of the same id equal 
            in value
        """
        
        # check if enabled
        if not self.bfit.fit_files.set_as_group.get():
            return 

        # set 
        self.bfit.fit_files.set_lines(pname=self.pname, 
                                      col=col, 
                                      value=self.variable[col].get())
        
    # ======================================================================= #
    def _unfix(self, *args):
        """
            disallow fixed shared parameters
        """
        if self.variable['shared'].get():
            self.variable['fixed'].set(False)
    
    # ======================================================================= #
    def _unshare(self, *args):
        """
            disallow fixed shared parameters
        """
        if self.variable['fixed'].get():
            self.variable['shared'].set(False)

    # ======================================================================= #
    def assign_shared(self):
        """
            Link the shared values
        """        
        
        # no key
        if not self.pname:
            return
        
        # get dict of shared boolean var
        share_var = self.bfit.fit_files.share_var
        
        # check if key is present
        if self.pname not in share_var.keys():
            self.bfit.fit_files.share_var[self.pname] = self.variable['shared']
            
        # assign key
        else:
            self.variable['shared'] = share_var[self.pname]
            
            share = self.variable['shared']
            share.trace_id = share.trace("w", self._unfix)
            share.trace_callback = self._unfix
            
        # link to checkbox
        self.entry['shared'].config(variable=self.variable['shared'])
        
    # ======================================================================= #
    def degrid(self):
        """
            Remove the entries
        """
        self.label.destroy()
        
        for i, key in enumerate(self.columns):
            self.entry[key].destroy()
            
    # ======================================================================= #
    def get(self, col):
        """
            get values
        
            col: str, name of column to get
        """
        
        if col in self.variable.keys():
            v = self.variable[col].get()
            
        if type(v) is str:
            v = float(v)
            
        return v

    # ======================================================================= #
    def grid(self, row):
        """
            Grid the entries
        """
        self.label.grid(column=0, row=row, sticky='e')
        
        for i, key in enumerate(self.columns):
            
            if not row == 2 and key == 'chi':
                pass
            elif key == 'chi':
                self.entry[key].grid(column=i+1, row=row, rowspan=100, padx=5)
            else:
                self.entry[key].grid(column=i+1, row=row, padx=5)     
        
    # ======================================================================= #
    def set(self, pname=None, **values):
        """
            set values
        
            pname: string, parameter name (ex: 1_T1)
            values: keyed by self.columns, the numerical or boolean values for each 
                    column to take
        """
        
        # label
        if pname is not None:
            self.pname = pname
            self.label.config(text=pname)

        for k, v in values.items():
            v = str(v)                
            
            # don't set
            if v == 'nan':
                continue
                
            # set
            if v in ('True', 'False'):
                self.variable[k].set(v=='True')
            else:
                self.variable[k].set(v)
