# fetch_files tab for bfit
# Derek Fujimoto
# Nov 2017

from tkinter import *
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
from bdata import bdata
import datetime
from functools import partial
import matplotlib.pyplot as plt

__doc__="""
    To-do:
        scrollbar for lots of runs selected
    """

# =========================================================================== #
# =========================================================================== #
class fetch_files(object):
    """
        Data fields:
            year: StringVar of year to fetch runs from 
            run: StringVar input to fetch runs.
            data: dictionary of bdata obj, keyed by run number
            bfit: pointer to parent class
            data_lines: dictionary of dataline obj, keyed by run number
            fet_entry_frame: frame of fetch tab
            check_rebin: IntVar for handling rebin aspect of checkall
            check_bin_remove: StringVar for handing omission of 1F data
            check_state: BooleanVar for handling check all
    """
    
    runmode_relabel = {'20':'SLR','1f':'1F','2e':'2e','1n':'Rb Cell Scan'}
    run_number_starter_line = '40001 40005-40010 (run numbers)'
    bin_remove_starter_line = '1 5 100-200 (omit bins)'
    
    # ======================================================================= #
    def __init__(self,fetch_data_tab,bfit):
        
        # initialize
        self.bfit = bfit
        self.data = {}
        self.data_lines = {}
        self.fit_input_tabs = {}
        self.check_rebin = IntVar()
        self.check_bin_remove = StringVar()
        self.check_state = BooleanVar()
        self.fetch_data_tab = fetch_data_tab
        
        # Fetch Tab ---------------------------------------------------------
        fet_entry_frame = ttk.Labelframe(fetch_data_tab,text='Specify Files')
        self.year = StringVar()
        self.run = StringVar()
        
        self.year.set(datetime.datetime.now().year)
        
        entry_year = ttk.Entry(fet_entry_frame,\
                textvariable=self.year,width=5)
        entry_run = ttk.Entry(fet_entry_frame,\
                textvariable=self.run,width=60)
        entry_run.insert(0,self.run_number_starter_line)
        entry_fn = partial(on_entry_click,text=self.run_number_starter_line,\
                            entry=entry_run)
        on_focusout_fn = partial(on_focusout,text=self.run_number_starter_line,\
                            entry=entry_run)
        entry_run.bind('<FocusIn>', entry_fn)
        entry_run.bind('<FocusOut>', on_focusout_fn)
        entry_run.config(foreground='grey')
        
        # fetch and clear button
        fetch = ttk.Button(fet_entry_frame,text='Fetch',command=self.get_data)
        
        # grid and labels
        fet_entry_frame.grid(column=0,row=0,sticky=(N,E))
        ttk.Label(fet_entry_frame,text="Year:").grid(column=0,row=0,\
                sticky=(E))
        entry_year.grid(column=1,row=0,sticky=(E))
        ttk.Label(fet_entry_frame,text="Run Number:").grid(column=2,row=0,\
                sticky=(E))
        entry_run.grid(column=3,row=0,sticky=(E))
        fetch.grid(column=4,row=0,sticky=(E))
        
        # padding 
        for child in fet_entry_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        
        # detected run mode label 
        runmode_label_frame = ttk.Labelframe(fetch_data_tab,pad=(10,5,10,5),\
                text='Run Mode',)
        
        self.runmode_label = ttk.Label(runmode_label_frame,text="",font='bold',justify=CENTER)
        
        # bigright frame : hold everything on the right
        bigright_frame = ttk.Frame(fetch_data_tab,pad=5)
        
        # rightframe
        right_frame = ttk.Labelframe(bigright_frame,\
                text='Operations on Checked Items',pad=5)
        
        check_remove = ttk.Button(right_frame,text='Remove',\
                command=self.remove_all,pad=5)
        check_draw = ttk.Button(right_frame,text='Draw',\
                command=self.draw_all,pad=5)
        
        check_set = ttk.Button(right_frame,text='Set',\
                command=self.set_all)
        check_rebin_label = ttk.Label(right_frame,text="SLR Rebin:",pad=5)
        check_rebin_box = Spinbox(right_frame,from_=1,to=100,width=3,\
                textvariable=self.check_rebin)
        check_bin_remove_entry = ttk.Entry(right_frame,\
                textvariable=self.check_bin_remove,width=20)
        check_all_box = ttk.Checkbutton(right_frame,text='Check all',\
            variable=self.check_state,onvalue=True,offvalue=False,pad=5,\
            command=self.check_all)
        self.check_state.set(False)
        
        # add grey to check_bin_remove_entry
        check_bin_remove_entry.insert(0,self.bin_remove_starter_line)
        
        check_entry_fn = partial(on_entry_click,\
                text=self.bin_remove_starter_line,\
                entry=check_bin_remove_entry)
        
        check_on_focusout_fn = partial(on_focusout,\
                text=self.bin_remove_starter_line,\
                entry=check_bin_remove_entry)
        
        check_bin_remove_entry.bind('<FocusIn>', check_entry_fn)
        check_bin_remove_entry.bind('<FocusOut>', check_on_focusout_fn)
        check_bin_remove_entry.config(foreground='grey')
                
        # grid
        runmode_label_frame.grid(column=1,row=0,sticky=(W,E))
        self.runmode_label.grid(column=0,row=0,sticky=(W,E))
        
        bigright_frame.grid(column=1,row=1,sticky=(E,N))
        
        right_frame.grid(column=0,row=0,sticky=(N))
        check_all_box.grid(         column=0,row=0,sticky=(N))
        check_remove.grid(          column=1,row=2,sticky=(N))
        check_draw.grid(            column=0,row=2,sticky=(N))
        check_rebin_label.grid(     column=0,row=3)
        check_rebin_box.grid(       column=1,row=3)
        check_bin_remove_entry.grid(column=0,row=4,sticky=(N))
        check_set.grid(             column=0,row=5,sticky=(N))
        
        bigright_frame.grid(rowspan=20)
        check_all_box.grid(columnspan=2)
        check_bin_remove_entry.grid(columnspan=2)
        check_set.grid(columnspan=2)
        
        check_rebin_box.grid_configure(padx=5,pady=5)
        check_rebin_label.grid_configure(padx=5,pady=5)
        check_set.grid_configure(padx=5,pady=5)
        
        # drawing style
        style_frame = ttk.Labelframe(bigright_frame,text='Drawing Quantity',\
                pad=5)
        entry_asym_type = ttk.Combobox(style_frame,\
                textvariable=self.bfit.fileviewer.asym_type,state='readonly',\
                width=15)
        entry_asym_type['values'] = self.bfit.fileviewer.asym_dict_keys
        
        style_frame.grid(column=0,row=1,sticky=(W,N))
        entry_asym_type.grid(column=0,row=0,sticky=(N))
        entry_asym_type.grid_configure(padx=24)
        
        # passing
        self.entry_run = entry_run
        self.entry_year = entry_year
        self.check_rebin_box = check_rebin_box
        self.check_bin_remove_entry = check_bin_remove_entry
        self.check_all_box = check_all_box
        
    # ======================================================================= #
    def check_all(self):
        """Check all tickboxes"""
        state = self.check_state.get()
        for k in self.data_lines.keys():
            self.data_lines[k].check_state.set(state)
    
    # ======================================================================= #
    def draw_all(self):
        
        # condense drawing into a funtion
        def draw_lines():
            for r in self.data_lines.keys():
                if self.data_lines[r].check_state.get():
                    self.data_lines[r].draw()
                
        # get draw style
        style = self.bfit.draw_style.get()
        
        # make new figure, draw stacked
        if style == 'stack':
            plt.figure()
            draw_lines()
            
        # overdraw in current figure, stacked
        elif style == 'redraw':
            plt.clf()
            self.bfit.draw_style.set('stack')
            draw_lines()
            self.bfit.draw_style.set('redraw')
            
        # make new figure, draw single
        elif style == 'new':
            draw_lines()
        else:
            raise ValueError("Draw style not recognized")

    # ======================================================================= #
    def export(self):
        """Export all data files as csv"""
        
        # filename
        filename = self.bfit.fileviewer.default_export_filename
        filename = filedialog.askdirectory()+'/'+filename
        
        # get data and write
        for k in self.data.keys():
            d = self.data[k]
            self.bfit.export(d,filename%(d.year,d.run))
    
    # ======================================================================= #
    def get_data(self):
        """Split data into parts, and assign to dictionary."""
        
        # make list of run numbers, replace possible deliminators
        try:
            run_numbers = self.string2run(self.run.get())
        except ValueError:
            return
        
        # get data
        data = {}
        for r in run_numbers:
            try:
                data[r] = bdata(r,year=int(self.year.get()))
            except RuntimeError:
                print("Failed to open run %d (%d)" % (r,int(self.year.get())))
        
        # check that data is all the same runtype
        run_types = []
        for k in self.data.keys():
            run_types.append(self.data[k].mode)
        for k in data.keys():
            run_types.append(data[k].mode)
            
        # different run types: select all runs of same type
        if not all([r==run_types[0] for r in run_types]):
            
            # unique run modes
            run_type_unique = np.unique(run_types)
            
            # message
            message = "Multiple run types detected:\n("
            for m in run_type_unique: 
                message += m+', '
            message = message[:-2]
            message += ')\n\nSelecting ' + run_types[0] + ' runs.'
            messagebox.showinfo(message=message)
            
        # get only run_types[0]
        for k in data.keys():
            if data[k].mode == run_types[0]:
                self.data[k] = data[k]
        self.runmode = run_types[0]
        self.runmode_label['text'] = self.runmode_relabel[run_types[0]]
        
        keys_list = list(self.data.keys())
        keys_list.sort()
        
        # make lines
        n = 1
        for r in keys_list:
            if r in self.data_lines.keys():
                self.data_lines[r].grid(n)
            else:
                self.data_lines[r] = dataline(self.bfit,self.data,\
                        self.data_lines,self.fetch_data_tab,self.data[r],n)
            n+=1
        self.bfit.fit_files.populate()
        
    # ======================================================================= #
    def remove_all(self):
        """Remove all data files from self.data_lines"""
        del_list = []
        for r in self.data_lines.keys():
            if self.data_lines[r].check_state.get():
                del_list.append(self.data_lines[r])
        for d in del_list:
            d.remove()
    
    # ======================================================================= #
    def return_binder(self):
        """Switch between various functions of the enter button. """
        
        # check where the focus is
        focus_id = str(self.bfit.root.focus_get())
        
        # run or year entry
        if focus_id in [str(self.entry_run), str(self.entry_year)]:
            self.get_data()
        
        # checked rebin or checked run omission
        elif focus_id in [str(self.check_rebin_box),\
                          str(self.check_bin_remove_entry)]:
            self.set_all()
        elif focus_id == str(self.check_all_box):
            self.draw_all()
        else:
            pass

    # ======================================================================= #
    def set_all(self):
        """Set a particular property for all checked items. """
        
        # check all file lines
        for r in self.data_lines.keys():
            
            # if checked
            if self.data_lines[r].check_state.get():
                
                # get values to enter
                self.data_lines[r].rebin.set(self.check_rebin.get())
                new_text = self.check_bin_remove.get()
                
                # check for greyed text
                if new_text != self.bin_remove_starter_line:
                    self.data_lines[r].bin_remove.set(new_text)
                else:
                    self.data_lines[r].bin_remove.set("")
                    
                # generate focus out event: trigger grey text reset
                self.data_lines[r].bin_remove_entry.event_generate('<FocusOut>')

    # ======================================================================= #
    def string2run(self,string):
        """Parse string, return list of run numbers"""
        
        full_string = string.replace(',',' ').replace(';',' ')
        full_string = full_string.replace(':','-')
        part_string = full_string.split()
        
        run_numbers = []
        for s in part_string:
            if '-' in s:
                try:
                    rn_lims = [int(s2) for s2 in s.split('-')]
                except ValueError:
                    run_numbers.append(int(s.replace('-','')))
                else:
                    rns = np.arange(rn_lims[0],rn_lims[1]+1).tolist()
                    run_numbers.extend(rns)
            else:
                run_numbers.append(int(s))
        # sort
        run_numbers.sort()
        
        if len(run_numbers) > 50:
            raise RuntimeWarning("Too many files selected (max 50).")
        return run_numbers
        
# =========================================================================== #
# =========================================================================== #
class dataline(object):
    """
        A line of objects to display run properties and remove bins and whatnot.
    """
        
    bin_remove_starter_line = '1 5 100-200 (omit bins)'
    
    # ======================================================================= #
    def __init__(self,bfit,datalist,lines_list,fetch_tab_frame,bd,row):
        """
            Inputs:
                fetch_tab_frame: parent in which to place line
                bd: bdata object corresponding to the file which is placed here. 
                row: where to grid this object
        """
        
        # variables
        self.bin_remove = StringVar()
        self.rebin = IntVar()
        self.check_state = BooleanVar()
        self.mode = bd.mode
        self.run = bd.run
        self.year = bd.year
        self.row = row
        self.bfit = bfit
        self.datalist = datalist # fetch_files.data
        self.lines_list = lines_list
        
        # temperature
        try:
            self.temperature = int(np.round(bd.camp.smpl_read_A.mean))
        except AttributeError:
            self.temperature = -1
            
        # field
        try:
            if bd.area == 'BNMR':
                self.field = np.around(bd.camp.b_field.mean,2)
                field_text = "%.2f T"%self.field
            else:
                self.field = np.around(bd.camp.hh_current.mean,2)
                field_text = "%.2f A"%self.field
        except AttributeError:
            self.field = -1
            field_text = ' '*6
        try:
            if bd.area == 'BNMR':
                self.bias = np.around(bd.epics.nmr_bias_p.mean,2)
            else:
                self.bias = np.around(bd.epics.nqr_bias.mean,2)/1000.
                
            if self.bias > 0:
                bias_text = "%.2f kV"%self.bias
            else:
                bias_text = "% .2f kV"%self.bias
        except AttributeError:
            self.bias = -1
            bias_text = ' '*7
        
        # build objects
        line_frame = ttk.Frame(fetch_tab_frame,pad=(5,0))
        year_label = ttk.Label(line_frame,text="%d"%self.year,pad=5)
        run_label = ttk.Label(line_frame,text="%d"%self.run,pad=5)
        temp_label = ttk.Label(line_frame,text="%3d K"%self.temperature,pad=5)
        field_label = ttk.Label(line_frame,text=field_text,pad=5)
        bias_label = ttk.Label(line_frame,text=bias_text,pad=5)
        bin_remove_entry = ttk.Entry(line_frame,textvariable=self.bin_remove,\
                width=20)
        remove_button = ttk.Button(line_frame,text='Remove',\
                command=self.remove,pad=5)
        draw_button = ttk.Button(line_frame,text='Draw',command=self.draw,pad=5)
        
        rebin_label = ttk.Label(line_frame,text="Rebin:",pad=5)
        rebin_box = Spinbox(line_frame,from_=1,to=100,width=3,\
                textvariable=self.rebin)
                
        self.check_state.set(False)
        check = ttk.Checkbutton(line_frame,text='',variable=self.check_state,\
                onvalue=True,offvalue=False,pad=5)
         
        # add grey text to bin removal
        bin_remove_entry.insert(0,self.bin_remove_starter_line)
        entry_fn = partial(on_entry_click,\
                text=self.bin_remove_starter_line,entry=bin_remove_entry)
        on_focusout_fn = partial(on_focusout,\
                text=self.bin_remove_starter_line,entry=bin_remove_entry)
        bin_remove_entry.bind('<FocusIn>', entry_fn)
        bin_remove_entry.bind('<FocusOut>', on_focusout_fn)
        bin_remove_entry.config(foreground='grey')
                
        # grid
        year_label.grid(column=1,row=0,sticky=E)
        run_label.grid(column=2,row=0,sticky=E)
        temp_label.grid(column=3,row=0,sticky=E)
        field_label.grid(column=4,row=0,sticky=E)
        bias_label.grid(column=5,row=0,sticky=E)
        if self.mode in ['1f','1n']: 
            bin_remove_entry.grid(column=6,row=0,sticky=E)
        if self.mode == '20': 
            rebin_label.grid(column=6,row=0,sticky=E)
            rebin_box.grid(column=7,row=0,sticky=E)
        check.grid(column=8,row=0,sticky=E)
        draw_button.grid(column=9,row=0,sticky=E)
        remove_button.grid(column=10,row=0,sticky=E)
        
        # passing
        self.line_frame = line_frame
        self.bin_remove_entry = bin_remove_entry
        
        # grid frame
        self.grid(row)
        
    # ======================================================================= #
    def grid(self,row):
        """Re-grid a dataline object so that it is in order by run number"""
        self.row = row
        self.line_frame.grid(column=0,row=row,columnspan=2, sticky=(W,N))
        
    # ======================================================================= #
    def remove(self):
        """Remove displayed dataline object from file selection. """
        
        # kill buttons and fram
        for child in self.line_frame.winfo_children():
            child.destroy()
        for child in self.line_frame.winfo_children():
            child.destroy()
        self.line_frame.destroy()
        
        # get rid of data
        del self.datalist[self.run]
        del self.lines_list[self.run]
        
        self.bfit.fit_files.populate()
                
    # ======================================================================= #
    def draw(self):
        """Draw single data file."""
        d = self.bfit.fileviewer.asym_type.get()
        d = self.bfit.fileviewer.asym_dict[d]
        
        if self.bin_remove.get() == self.bin_remove_starter_line:
            self.bfit.draw(self.datalist[self.run],d,self.rebin.get())
        else:
            self.bfit.draw(self.datalist[self.run],d,self.rebin.get(),\
                option=self.bin_remove.get())
        
# =========================================================================== #
def on_entry_click(event,entry,text):
    """Vanish grey text on click"""
    if entry.get() == text:
        entry.delete(0, "end") # delete all the text in the entry
        entry.insert(0, '') #Insert blank for user input
        entry.config(foreground = 'black')

# =========================================================================== #
def on_focusout(event,entry,text):
    """Set grey text for boxes on exit"""
    if entry.get() == '':
        entry.insert(0,text)
        entry.config(foreground = 'grey')
    else:
        entry.config(foreground = 'black')



