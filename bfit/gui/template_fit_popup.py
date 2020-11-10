
# Model the fit results with a function
# Derek Fujimoto
# August 2019

from tkinter import *
from tkinter import ttk, messagebox

import logging, re, os, warnings
import weakref as wref
import numpy as np
import pandas as pd

from bfit import logger_name
from bfit.backend.entry_color_set import on_focusout,on_entry_click
from bfit.backend.raise_window import raise_window
import bfit.backend.colors as colors

# ========================================================================== #
class template_fit_popup(object):
    """
        Base class for fitting popup windows 
        
        bfit
        fittab
        logger
        
        entry:              Text, text entry for user
        entry_label:        Label, instructions above input text box
        input_fn_text:      string, text defining input functions
        left_frame:         Frame, for additional details 
        new_par:            dataframe, index: parnames, columns: p0,blo,bhi,res,err
        
        output_par_text     text, detected parameter names
        output_text         dict, keys: p0,blo,bhi,res,err, value: tkk.Text objects
       
        output_par_text_val string, contents of output_par_text
        output_text_val     dict of strings, contents of output_text
       
        reserved_pars:      dict, define values in bdata that can be accessed
        win:                Toplevel
    """
    
    # default parameter values on new parameter
    default_parvals = { 'p0':1,
                        'blo':-np.inf,
                        'bhi':np.inf,
                        'res':np.nan,
                        'err':np.nan}
    
    window_title = 'Base class popup window'

    # ====================================================================== #
    def __init__(self, bfit, input_fn_text='', output_par_text='', output_text=''):
        
        self.bfit = bfit
        self.fittab = bfit.fit_files
        
        self.input_fn_text = input_fn_text
        self.output_par_text_val = output_par_text
        
        if not output_text:
            self.output_text_val = {}
        else:
            self.output_text_val = output_text
    
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title(self.window_title)
        frame = ttk.Frame(self.win, relief='sunken',pad=5)
        left_frame = ttk.Frame(frame)
        right_frame = ttk.Frame(frame)

        # set icon
        try:
            img = PhotoImage(file=os.path.dirname(__file__)+'/../images/icon.gif')
            self.win.tk.call('wm', 'iconphoto', self.win._w, img)
        except Exception as err:
            print(err)

        # Key bindings
        self.win.bind('<Control-Key-Return>',self.do_fit)
        self.win.bind('<Control-Key-KP_Enter>',self.do_fit)
        
        # Text entry
        entry_frame = ttk.Frame(right_frame,relief='sunken',pad=5)
        self.entry_label = ttk.Label(entry_frame,justify=LEFT,
                                text='')
        self.entry = Text(entry_frame,width=60,height=13,state='normal')
        self.entry.bind('<KeyRelease>',self.get_input)
        scrollb = Scrollbar(entry_frame, command=self.entry.yview)
        self.entry['yscrollcommand'] = scrollb.set
        
        # Insert default text
        self.entry.insert('1.0',self.input_fn_text.strip())
        
        # text for output
        output_frame = ttk.Frame(right_frame,relief='sunken',pad=5)
        output_head1_label = ttk.Label(output_frame,text='Par Name')
        output_head2_label = ttk.Label(output_frame,text='p0')
        output_head3_label = ttk.Label(output_frame,text='Bounds')
        output_head4_label = ttk.Label(output_frame,text='Result')
        output_head5_label = ttk.Label(output_frame,text='Error (-)')
        output_head6_label = ttk.Label(output_frame,text='Error (+)')
        self.output_par_text = Text(output_frame,width=8,height=8)
        self.output_text = {k:Text(output_frame,width=8,height=8,wrap='none')\
                            for k in ('p0','blo','bhi','res','err-','err+')}
        
        # default starter strings
        if self.output_par_text_val: 
            self.output_par_text.insert('1.0',self.output_par_text_val)
        self.output_par_text.config(state='disabled')
    
        if self.output_text_val: 
            for k in self.output_text_val:
                self.output_text[k].insert('1.0',self.output_text_val[k])

        # disable results
        for k in ('res','err-','err+'):
            self.output_text[k].config(state='disabled',width=12)

        # key bindings and scrollbar
        scrollb_out = Scrollbar(output_frame, command=self.yview)
        self.output_par_text['yscrollcommand'] = scrollb_out.set
        for k in self.output_text:
            self.output_text[k].bind('<KeyRelease>',self.get_result_input)
            self.output_text[k]['yscrollcommand'] = scrollb_out.set
                
        c = 0; r = 0;
        output_head1_label.grid(column=c,row=r);        c+=1;
        output_head2_label.grid(column=c,row=r);        c+=1;
        output_head3_label.grid(column=c,row=r,
                                columnspan=2);          c+=2;
        output_head4_label.grid(column=c,row=r);        c+=1;
        output_head5_label.grid(column=c,row=r);        c+=1;
        output_head6_label.grid(column=c,row=r);        c+=1;
        
        c = 0; r += 1;
        self.output_par_text.grid(column=c,row=r,sticky=N); c+=1;
        for k in ('p0','blo','bhi','res','err-','err+'):
            self.output_text[k].grid(column=c,row=r,sticky=N); c+=1;
        scrollb_out.grid(row=r, column=c, sticky='nsew')
        
        # fitting button 
        fit_button = ttk.Button(right_frame,text='Fit',command=self.do_fit)
        
        # gridding
        self.entry_label.grid(column=0,row=0,sticky=W)
        self.entry.grid(column=0,row=1)
        scrollb.grid(row=1, column=1, sticky='nsew')
        
        # grid to frame
        frame.grid(column=0,row=0)
        left_frame.grid(column=0,row=0,sticky=(N,S))
        right_frame.grid(column=1,row=0,sticky=(N,S))
        
        entry_frame.grid(column=0,row=0,sticky=(N,E,W),padx=1,pady=1)
        output_frame.grid(column=0,row=1,sticky=(N,E,W,S),padx=1,pady=1)
        fit_button.grid(column=0,row=2,sticky=(N,E,W),padx=1,pady=1)
        
        # initialize 
        self.new_par = pd.DataFrame(columns=['name','p0','blo','bhi','res','err-','err+']) 
        self.left_frame = left_frame
        
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
    
    # ====================================================================== #
    def _do_fit(self,text):
        """
            Do the fitting. Called by do_fit_setup().
            
            output: (par,cov,chi,gchi)
        """
        pass
    
    # ====================================================================== #
    def do_fit(self,*args):
        """
            Set up the fit functions and do the fit. 
            Then map the outputs to the proper displays. 
        """
        
        # parse text
        self.do_parse()
        
        # clean input
        text = self.input_fn_text.split('\n')
        text = [t.strip() for t in text if '=' in t]
        
        # check for no input
        if not text:    return
    
        # do the fit and kill fitting window
        fit_status_window = self.bfit.fit_files.make_fit_status_window()
        try:
            # do the fit
            par, std_l, std_h = self._do_fit(text)
        except Exception as errmsg:
            raise errmsg from None
        finally:
            fit_status_window.destroy()
            del fit_status_window
        
        # display output for global parameters
        for i in self.new_par.index:
            self.new_par.loc[i,'res'] = par[i]
            self.new_par.loc[i,'err-'] = std_l[i]
            self.new_par.loc[i,'err+'] = std_h[i]
        self.set_par_text()
        
    # ====================================================================== #
    def do_parse(self,*args):
        """
            Detect new global variables
            returns split lines, new parameter names 
        """
        
        # clean input
        text = self.input_fn_text.split('\n')
        text = [t.strip() for t in text if '=' in t]
        
        # check for no input
        if not text:
            return
        
        # get equations and defined variables
        defined = [t.split('=')[0].strip() for t in text]
        eqn = [t.split('=')[1].strip() for t in text]
        
        # check for new parameters
        new_par = []
        for eq in eqn:
            lst = re.split('\W+',eq)    # split list non characters
            
            # throw out known things: numbers numpy equations
            delist = []
            for i,l in enumerate(lst):
                
                # check numpy functions
                if l == 'np':
                    delist.append(i)
                    delist.append(i+1)
                    continue
                
                # check integer
                try: 
                    int(l)
                except ValueError:
                    pass
                else:
                    delist.append(i)
                    continue
                
                # check variables
                if l in self.reserved_pars:  
                    delist.append(i)
                    continue
                    
            delist.sort()
            for i in delist[::-1]:
                try:
                    del lst[i]
                except IndexError:  # error raised on incomplete math: ex "np."
                    pass
                
            new_par.append(lst)

        # add result
        new_par = np.unique(np.concatenate(new_par))
        for k in new_par:
            
            # bad input
            if not k: continue
            
            # set defaults
            if k not in self.new_par['name'].values:
                self.new_par = self.new_par.append({'name':k,**self.default_parvals},
                                                   ignore_index=True)
        
        # drop results 
        for i,k in zip(self.new_par.index,self.new_par['name']):
            if k not in new_par:
                self.new_par.drop(i,inplace=True)
        
        # set fields
        self.new_par.sort_values('name',inplace=True)
        self.set_par_text()
        
        # logging
        self.logger.info('Parse found constraints for %s, and defined %s',
                         sorted(defined),
                         self.new_par['name'].values.tolist())
    
    # ====================================================================== #
    def get_input(self,*args):
        """Get input from text box."""
        self.input_fn_text = self.entry.get('1.0',END)
        self.do_parse()
        
    # ====================================================================== #
    def get_result_input(self,*args):
        """
            Set new_par row to match changes made by user
        """
    
        # get text
        try:
            text = {k : list(map(float, self.output_text[k].get('1.0', END).split('\n')[:-1])) \
                for k in self.output_text}
        # no update if blank
        except ValueError:
            return 
        
        # dataframe it
        try:
            text = pd.DataFrame(text)   
        # bad input
        except ValueError:
            return
        
        # get names of the parameters
        parnames = self.output_par_text.get('1.0', END).split('\n')[:-1]
        
        # update
        par = self.new_par.set_index('name')
        for i,name in enumerate(parnames):
            par.loc[name] = text.iloc[i]
        par.reset_index(inplace=True)
        self.new_par = par
        self.logger.debug('get_result_input: updated new_par')
    
    # ====================================================================== #
    def set_par_text(self):
        """
            Set the textboxes based on stored results in self.newpar
        """
        
        # get strings
        set_par = self.new_par.astype(str)
        
        # round
        numstr = '%'+('.%df' % self.bfit.rounding)
        for k in ('res', 'err-', 'err+'):
            set_par[k] = set_par.loc[:, k].apply(\
                    lambda x : numstr % np.around(float(x), self.bfit.rounding))
        
        # enable setting
        for k in ('res','err-','err+'):
            self.output_text[k].config(state='normal')
        self.output_par_text.config(state='normal')
        
        self.output_par_text.delete('1.0', END)
        self.output_par_text.insert(1.0, '\n'.join(set_par['name']))
        self.output_par_text_val = '\n'.join(set_par['name'])
        
        for k in self.output_text:
            self.output_text[k].delete('1.0', END)
            self.output_text[k].insert(1.0,'\n'.join(set_par[k]))
            self.output_text_val[k] = '\n'.join(set_par[k])
                
        # disable setting
        for k in ('res', 'err-', 'err+'):
            self.output_text[k].config(state='disabled')
        self.output_par_text.config(state='disabled')
        
    # ====================================================================== #
    def yview(self,*args):
        """
            Scrollbar for all output text fields
        """
        self.output_par_text.yview(*args)
        for k in self.output_text:
            self.output_text[k].yview(*args)
