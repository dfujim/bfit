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
from bfit.gui.fitdata import fitdata

__doc__="""
    To-do:
        scrollbar for lots of runs selected
    """

# =========================================================================== #
# =========================================================================== #
class fetch_files(object):
    """
        Data fields:
            
            canvas_frame_id: id number of frame in canvas
            check_rebin: IntVar for handling rebin aspect of checkall
            check_bin_remove: StringVar for handing omission of 1F data
            check_state: BooleanVar for handling check all
            
            
            data_canvas: canvas object allowing for scrolling 
            dataline_frame: frame holding all the data lines. Exists as a window
                in the data_canvas
            
            entry_asym_type: combobox for asym calc and draw type
            year: StringVar of year to fetch runs from 
            run: StringVar input to fetch runs.
            bfit: pointer to parent class
            data_lines: dictionary of dataline obj, keyed by run number
            fet_entry_frame: frame of fetch tab
            runmode_label: display run mode
            runmode: display run mode string
            max_number_fetched: max number of files you can fetch
    """
    
    runmode_relabel = {'20':'Spin-Lattice Relaxation (20)',
                       '1f':'Frequency Scan (1f)',
                       '2e':'Randomized Frequency (2e)',
                       '1n':'Rb Cell Scan (1n)',
                       '2h':'Alpha Tagging/Diffusion (2h)'}
    run_number_starter_line = '40001 40005-40010 (run numbers)'
    bin_remove_starter_line = '1 5 100-200 (omit bins)'
    max_number_fetched = 500
    
    # ======================================================================= #
    def __init__(self,fetch_data_tab,bfit):
        
        # initialize
        self.bfit = bfit
        self.data_lines = {}
        self.fit_input_tabs = {}
        self.check_rebin = IntVar()
        self.check_bin_remove = StringVar()
        self.check_state = BooleanVar()
        self.fetch_data_tab = fetch_data_tab
        
        # Frame for specifying files -----------------------------------------
        fet_entry_frame = ttk.Labelframe(fetch_data_tab,text='Specify Files')
        self.year = StringVar()
        self.run = StringVar()
        
        self.year.set(datetime.datetime.now().year)
        
        entry_year = ttk.Entry(fet_entry_frame,textvariable=self.year,width=5)
        entry_run = ttk.Entry(fet_entry_frame,textvariable=self.run,width=80)
        entry_run.insert(0,self.run_number_starter_line)
        entry_fn = partial(on_entry_click,text=self.run_number_starter_line,\
                            entry=entry_run)
        on_focusout_fn = partial(on_focusout,text=self.run_number_starter_line,\
                            entry=entry_run)
        entry_run.bind('<FocusIn>', entry_fn)
        entry_run.bind('<FocusOut>', on_focusout_fn)
        entry_run.config(foreground='grey')
        
        # fetch button
        fetch = ttk.Button(fet_entry_frame,text='Fetch',command=self.get_data)
        
        # grid and labels
        fet_entry_frame.grid(column=0,row=0,sticky=(N,W))
        ttk.Label(fet_entry_frame,text="Year:").grid(column=0,row=0,sticky=W)
        entry_year.grid(column=1,row=0,sticky=(W))
        ttk.Label(fet_entry_frame,text="Run Number:").grid(column=2,row=0,sticky=W)
        entry_run.grid(column=3,row=0,sticky=W)
        fetch.grid(column=4,row=0,sticky=E)
        
        # padding 
        for child in fet_entry_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        
        # Frame for run mode -------------------------------------------------
        runmode_label_frame = ttk.Labelframe(fetch_data_tab,pad=(10,5,10,5),\
                text='Run Mode',)
        
        self.runmode_label = ttk.Label(runmode_label_frame,text="",font='bold',justify=CENTER)
        
        # Scrolling frame to hold datalines
        yscrollbar = Scrollbar(fetch_data_tab, orient=VERTICAL)         
        self.data_canvas = Canvas(fetch_data_tab,bd=0,              # make a canvas for scrolling
                yscrollcommand=yscrollbar.set,                      # scroll command receive
                scrollregion=(0, 0, 5000, 5000),confine=True)       # default size
        yscrollbar.config(command=self.data_canvas.yview)           # scroll command send
        dataline_frame = ttk.Frame(self.data_canvas,pad=5)          # holds 
        
        self.canvas_frame_id = self.data_canvas.create_window((0,0),    # make window which can scroll
                window=dataline_frame,
                anchor='nw')
        dataline_frame.bind("<Configure>",self.config_canvas) # bind resize to alter scrollable region
        self.data_canvas.bind("<Configure>",self.config_dataline_frame) # bind resize to change size of contained frame
        
        # Frame to hold everything on the right ------------------------------
        bigright_frame = ttk.Frame(fetch_data_tab,pad=5)
        
        # Frame for group set options ----------------------------------------
        right_frame = ttk.Labelframe(bigright_frame,\
                text='Operations on Checked Items',pad=30)
        
        check_remove = ttk.Button(right_frame,text='Remove',\
                command=self.remove_all,pad=5)
        check_draw = ttk.Button(right_frame,text='Draw Data',\
                command=self.draw_all,pad=5)
        check_draw_fits = ttk.Button(right_frame,text='Draw Fits',\
                command=self.draw_all_fits,pad=5)
        
        check_set = ttk.Button(right_frame,text='Set',\
                command=self.set_all)
        check_rebin_label = ttk.Label(right_frame,text="SLR Rebin:",pad=5)
        check_rebin_box = Spinbox(right_frame,from_=1,to=100,width=3,\
                textvariable=self.check_rebin)
        check_bin_remove_entry = ttk.Entry(right_frame,\
                textvariable=self.check_bin_remove,width=20)
        
        check_all_box = ttk.Checkbutton(right_frame,
                text='Force Check State',variable=self.check_state,
                onvalue=True,offvalue=False,pad=5,command=self.check_all)
        self.check_state.set(False)
                
        check_toggle_button = ttk.Button(right_frame,\
                text='Toggle All Check States',command=self.toggle_all,pad=5)
        
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
        runmode_label_frame.grid(column=2,row=0,sticky=(N,W,E))
        self.runmode_label.grid(column=0,row=0,sticky=(N,W,E))
        
        bigright_frame.grid(column=2,row=1,sticky=(N,E))
        
        self.data_canvas.grid(column=0,row=1,sticky=(E,W,S,N))
        yscrollbar.grid(column=1,row=1,sticky=(W,S,N))
        
        right_frame.grid(           column=0,row=0,sticky=(N,E,W))
        r = 0
        check_all_box.grid(         column=0,row=r,sticky=(N)); r+= 1
        check_toggle_button.grid(   column=0,row=r,sticky=(N),pady=10); r+= 1
        check_draw.grid(            column=0,row=r,sticky=(N))
        check_draw_fits.grid(       column=1,row=r,sticky=(N)); r+= 1
        check_remove.grid(          column=0,row=r,sticky=(N,E,W)); r+= 1
        check_rebin_label.grid(     column=0,row=r)
        check_rebin_box.grid(       column=1,row=r); r+= 1
        check_bin_remove_entry.grid(column=0,row=r,sticky=(N)); r+= 1
        check_set.grid(             column=0,row=r,sticky=(N))
        
        bigright_frame.grid(        rowspan=2,sticky=(N,E,W))
        check_all_box.grid(         columnspan=2)
        check_remove.grid(          columnspan=2)
        check_toggle_button.grid(   columnspan=2)
        check_bin_remove_entry.grid(columnspan=2)
        check_set.grid(             columnspan=2)
        
        check_rebin_box.grid_configure(padx=5,pady=5,sticky=(E,W))
        check_rebin_label.grid_configure(padx=5,pady=5,sticky=(E,W))
        check_set.grid_configure(padx=5,pady=5,sticky=(E,W))
        
        # resizing
        fetch_data_tab.grid_columnconfigure(0, weight=1)        # main area
        fetch_data_tab.grid_rowconfigure(1,weight=1)            # main area
        
        for i in range(3):
            if i%2 == 0:    fet_entry_frame.grid_columnconfigure(i, weight=2)
        fet_entry_frame.grid_columnconfigure(3, weight=1)
            
        self.data_canvas.grid_columnconfigure(0,weight=1)    # fetch frame 
        self.data_canvas.grid_rowconfigure(0,weight=1)
            
        # drawing style
        style_frame = ttk.Labelframe(bigright_frame,text='Drawing Quantity',\
                pad=5)
        self.entry_asym_type = ttk.Combobox(style_frame,\
                textvariable=self.bfit.fileviewer.asym_type,state='readonly',\
                width=20)
        self.entry_asym_type['values'] = ()
        
        style_frame.grid(column=0,row=1,sticky=(W,N))
        self.entry_asym_type.grid(column=0,row=0,sticky=(N))
        self.entry_asym_type.grid_configure(padx=24)
        
        # passing
        self.entry_run = entry_run
        self.entry_year = entry_year
        self.check_rebin_box = check_rebin_box
        self.check_bin_remove_entry = check_bin_remove_entry
        self.check_all_box = check_all_box
        self.dataline_frame = dataline_frame
    
    # ======================================================================= #
    def check_all(self):
        """Force all tickboxes to be in a given state"""
        for k in self.data_lines.keys():
            state = self.check_state.get()
            self.data_lines[k].check_state.set(state)
        
    # ======================================================================= #
    def config_canvas(self,event):
        """Alter scrollable region based on canvas bounding box size. 
        (changes scrollbar properties)"""
        self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all"))
    
    # ======================================================================= #
    def config_dataline_frame(self,event):
        """Alter size of contained frame in canvas. Allows for inside window to 
        be resized with mouse drag""" 
        self.data_canvas.itemconfig(self.canvas_frame_id,width=event.width)
        
    # ======================================================================= #
    def draw_all(self,ignore_check=False):
        """Draw all data in data lines"""
        # condense drawing into a funtion
        def draw_lines():
            for r in self.data_lines.keys():
                if self.data_lines[r].check_state.get() or ignore_check:
                    self.data_lines[r].draw()
                
        # get draw style
        style = self.bfit.draw_style.get()
        
        # make new figure, draw stacked
        if style == 'stack':
            draw_lines()
            
        # overdraw in current figure, stacked
        elif style == 'redraw':
            plt.clf()
            self.bfit.draw_style.set('stack')
            draw_lines()
            self.bfit.draw_style.set('redraw')
            
        # make new figure, draw single
        elif style == 'new':
            plt.figure()
            self.bfit.draw_style.set('stack')
            draw_lines()
            self.bfit.draw_style.set('new')
        else:
            messagebox.showerror(message="Draw style not recognized")
            raise ValueError("Draw style not recognized")

    # ======================================================================= #
    def draw_all_fits(self,ignore_check=False):
        """Draw all fits in data lines"""
        # condense drawing into a funtion
        def draw_lines():
            for r in self.data_lines.keys():
                line = self.data_lines[r] 
                if line.check_state.get() or ignore_check:
                    try:
                        self.bfit.fit_files.draw_fit(r,label=line.label.get())
                    except KeyError:
                        pass
                
        # get draw style
        style = self.bfit.draw_style.get()
        
        # make new figure, draw stacked
        if style == 'new':
            plt.figure()
            self.bfit.draw_style.set('stack')
            draw_lines()
            self.bfit.draw_style.set('new')
            
        elif style == 'stack':
            draw_lines()
            
        # overdraw in current figure, stacked
        elif style == 'redraw':
            plt.clf()
            self.bfit.draw_style.set('stack')
            draw_lines()
            self.bfit.draw_style.set('redraw')
            
        else:
            messagebox.showerror(message="Draw style not recognized")
            raise ValueError("Draw style not recognized")

    # ======================================================================= #
    def export(self):
        """Export all data files as csv"""
        
        # filename
        filename = self.bfit.fileviewer.default_export_filename
        try:
            filename = filedialog.askdirectory()+'/'+filename
        except TypeError:
            pass
        
        # get data and write
        for k in self.bfit.data.keys():
            d = self.bfit.data[k].bd
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
        s = ['Failed to open run']
        for r in run_numbers:
            try:
                data[r] = fitdata(self.bfit,bdata(r,year=int(self.year.get())))
            except (RuntimeError,ValueError):
                s.append("%d (%d)" % (r,int(self.year.get())))

        # print error message
        if len(s)>1:
            s = '\n'.join(s)
            print(s)
            messagebox.showinfo(message=s)
        
        # check that data is all the same runtype
        run_types = []
        for k in self.bfit.data.keys():
            run_types.append(self.bfit.data[k].mode)
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
                self.bfit.data[k] = data[k]
        
        try:
            self.runmode = run_types[0]
        except IndexError:
            messagebox.showerror(message='No valid runs detected.')
            raise RuntimeError('No valid runs detected.')
        self.runmode_label['text'] = self.runmode_relabel[self.runmode]
        self.bfit.set_asym_calc_mode_box(self.runmode)
        
        keys_list = list(self.bfit.data.keys())
        keys_list.sort()
        
        # make lines
        n = 1
        for r in keys_list:
            if r in self.data_lines.keys():
                self.data_lines[r].grid(n)
            else:
                self.data_lines[r] = dataline(self.bfit,\
                        self.data_lines,self.dataline_frame,self.bfit.data[r],n)
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
        
        if len(run_numbers) > self.max_number_fetched:
            raise RuntimeWarning("Too many files selected (max 50).")
        return run_numbers
    
    # ======================================================================= #
    def toggle_all(self):
        """Toggle all tickboxes"""
        for k in self.data_lines.keys():
            state = not self.data_lines[k].check_state.get()
            self.data_lines[k].check_state.set(state)

# =========================================================================== #
# =========================================================================== #
class dataline(object):
    """
        A line of objects to display run properties and remove bins and whatnot.
        
        bfit:           pointer to root 
        bin_remove:     StringVar for specifying which bins to remove in 1f runs
        bin_remove_entry: Entry object for bin remove 
        check_state:    BooleanVar for specifying check state
        group:          IntVar for fitting group ID
        label:          StringVar for labelling runs in legends
        line_frame:     Frame that object is placed in
        lines_list:     list of datalines
        mode:           bdata run mode
        rebin:          IntVar for SLR rebin
        row:            position in list
        run:            bdata run number
        year:           bdata year
        
        
    """
        
    bin_remove_starter_line = '1 5 100-200 (omit bins)'
    
    # ======================================================================= #
    def __init__(self,bfit,lines_list,fetch_tab_frame,bdfit,row):
        """
            Inputs:
                fetch_tab_frame: parent in which to place line
                bdfit: fitdata object corresponding to the file which is placed here. 
                row: where to grid this object
        """
        
        # variables
        self.bfit = bfit
        self.bin_remove = bdfit.omit
        self.label = bdfit.label
        self.rebin = bdfit.rebin
        self.group = bdfit.group
        self.check_state = bdfit.check_state
        self.mode = bdfit.mode
        self.run =  bdfit.run
        self.year = bdfit.year
        self.row = row
        self.lines_list = lines_list
        bd = bdfit.bd
        self.bdfit = bdfit
        
        # temperature
        try:
            self.temperature = int(np.round(bdfit.temperature.mean))
        except AttributeError:
            self.temperature = np.nan
                
        # field
        self.field = np.around(bdfit.field,2)
        
        try:
            field_text = "%.2f T"%self.field
        except TypeError:
            field_text = ' '
        
        # bias
        self.bias = self.bdfit.bias
        try:
            bias_text = "%.2f kV"%self.bias
        except TypeError:
            bias_text = ' '
        
        # build objects
        line_frame = ttk.Frame(fetch_tab_frame,pad=(5,0))
        year_label = ttk.Label(line_frame,text="%d"%self.year,pad=5)
        run_label = ttk.Label(line_frame,text="%d"%self.run,pad=5)
        temp_label = ttk.Label(line_frame,text="%3d K"%self.temperature,pad=5)
        field_label = ttk.Label(line_frame,text=field_text,pad=5)
        bias_label = ttk.Label(line_frame,text=bias_text,pad=5)
        bin_remove_entry = ttk.Entry(line_frame,textvariable=self.bin_remove,\
                width=20)
                
        label_label = ttk.Label(line_frame,text="Label:",pad=5)
        label_entry = ttk.Entry(line_frame,textvariable=self.label,\
                width=10)
                
        remove_button = ttk.Button(line_frame,text='Remove',\
                command=self.remove,pad=1)
        draw_button = ttk.Button(line_frame,text='Draw',command=self.draw,pad=1)
        self.draw_fit_button = ttk.Button(line_frame,text='Draw Fit',
                command= lambda : self.bfit.fit_files.draw_fit(run=self.run),
                pad=1,state=DISABLED)
        
        rebin_label = ttk.Label(line_frame,text="Rebin:",pad=5)
        rebin_box = Spinbox(line_frame,from_=1,to=100,width=3,\
                textvariable=self.rebin)
                
        group_label = ttk.Label(line_frame,text="Group:",pad=5)
        group_box = Spinbox(line_frame,from_=1,to=100,width=3,\
                textvariable=self.group)
                   
        self.check_state.set(bfit.fetch_files.check_state.get())
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
             
        # add grey text to label
        label = self.bfit.get_label(self.bfit.data[self.run])
        label_entry.insert(0,label)
        entry_fn_lab = partial(on_entry_click,text=label,
                               entry=label_entry)
        on_focusout_fn_lab = partial(on_focusout,text=label,
                                 entry=label_entry)
        label_entry.bind('<FocusIn>', entry_fn_lab)
        label_entry.bind('<FocusOut>', on_focusout_fn_lab)
        label_entry.config(foreground='grey')
                
        # grid
        c = 1
        check.grid(column=c,row=0,sticky=E); c+=1
        year_label.grid(column=c,row=0,sticky=E); c+=1
        run_label.grid(column=c,row=0,sticky=E); c+=1
        temp_label.grid(column=c,row=0,sticky=E); c+=1
        field_label.grid(column=c,row=0,sticky=E); c+=1
        bias_label.grid(column=c,row=0,sticky=E); c+=1
        if self.mode in ['1f','1n']: 
            bin_remove_entry.grid(column=c,row=0,sticky=E); c+=1
        if self.mode in ['20','2h']: 
            rebin_label.grid(column=c,row=0,sticky=E); c+=1
            rebin_box.grid(column=c,row=0,sticky=E); c+=1
        label_label.grid(column=c,row=0,sticky=E); c+=1
        label_entry.grid(column=c,row=0,sticky=E); c+=1
        group_label.grid(column=c,row=0,sticky=E); c+=1
        group_box.grid(column=c,row=0,sticky=E); c+=1
        draw_button.grid(column=c,row=0,sticky=E); c+=1
        self.draw_fit_button.grid(column=c,row=0,sticky=E); c+=1
        remove_button.grid(column=c,row=0,sticky=E); c+=1
        
        # resizing
        fetch_tab_frame.grid_columnconfigure(0, weight=1)   # big frame
        for i in (2,4,5,6):
            line_frame.grid_columnconfigure(i, weight=100)  # run info
        for i in (7,9,11):
            line_frame.grid_columnconfigure(i, weight=1)    # input labels
        
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
        self.line_frame.destroy()
        
        # get rid of data
        del self.bfit.data[self.run]
        del self.lines_list[self.run]
        
        # repopulate fit files tab
        self.bfit.fit_files.populate()
        
        # remove data from storage
        if len(self.lines_list) == 0:
            ff = self.bfit.fetch_files
            ff.runmode_label['text'] = ''
                
    # ======================================================================= #
    def draw(self):
        """Draw single data file."""
        
        # get new data file
        data = bdata(self.run,year=self.year)
        
        # get data file run type
        d = self.bfit.fileviewer.asym_type.get()
        d = self.bfit.fileviewer.asym_dict[d]
        
        if self.bin_remove.get() == self.bin_remove_starter_line:
            self.bfit.draw(data,d,self.rebin.get(),
                label=self.label.get())
        else:
            self.bfit.draw(data,d,self.rebin.get(),\
                option=self.bin_remove.get(),label=self.label.get())

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



