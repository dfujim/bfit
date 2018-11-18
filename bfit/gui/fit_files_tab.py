# fit_files tab for bfit
# Derek Fujimoto
# Dec 2017

from tkinter import *
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime, os, traceback

from functools import partial
from bfit.gui.zahersCalculator import current2field
from bdata import bdata

# =========================================================================== #
# =========================================================================== #
class fit_files(object):
    """
        Data fields:
            chi_threshold:  if chi > thres, set color to red
            draw_components:list of titles for labels, options to export, draw.
            file_tabs:      dictionary of fitinputtab objects, keyed by group number 
            fitter:         fitting object from self.bfit.routine_mod
            fit_function_title: title of fit function to use
            fit_function_title_box: spinbox for fit function names
            fit_input:      fitting input values = (fn_name,ncomp,data_list)
            groups:         group numbers from fetch tab
            mode:           what type of run is this. 
            n_component:    number of fitting components (IntVar)
            runbook:        notebook of fit inputs for runs
            runmode_label:  display run mode 
            set_as_group:   BooleanVar() if true, set fit parfor whole group
            xaxis:          StringVar() for parameter to draw on x axis
            yaxis:          StringVar() for parameter to draw on y axis
            xaxis_combobox: box for choosing x axis draw parameter
            yaxis_combobox: box for choosing y axis draw parameter
    """ 
    
    default_fit_functions = {'20':('Exp','Str Exp'),'2h':('Exp','Str Exp'),
            '1f':('Lorentzian','Gaussian'),'1n':('Lorentzian','Gaussian')}
    mode = ""
    chi_threshold = 1.5 # threshold for red highlight on bad fits 
    n_fitx_pts = 500    # number of points to draw in fitted curves
    
    # ======================================================================= #
    def __init__(self,fit_data_tab,bfit):
        
        # initialize
        self.file_tabs = {}
        self.bfit = bfit
        self.groups = []
        self.fit_output = {}
        self.fitter = self.bfit.routine_mod.fitter()
        self.draw_components = bfit.draw_components
            
        # make top level frames
        mid_fit_frame = ttk.Frame(fit_data_tab,pad=5)   # notebook
        right_frame = ttk.Labelframe(fit_data_tab,text='Fit Results',pad=5)     # draw fit results
        
        mid_fit_frame.grid(column=0,row=1,sticky=(N,W,E))
        right_frame.grid(column=1,row=1,columnspan=2,rowspan=2,sticky=(N,E,W))
        
        fit_data_tab.grid_columnconfigure(0,weight=1)   # fitting space
        fit_data_tab.grid_columnconfigure(1,weight=10)  # par select space
        
        # TOP FRAME 
        
        # fit function select 
        fn_select_frame_border = ttk.Labelframe(fit_data_tab,text='Fit Function')
        fn_select_frame = ttk.Frame(fn_select_frame_border)
        self.fit_function_title = StringVar()
        self.fit_function_title.set("")
        self.fit_function_title_box = ttk.Combobox(fn_select_frame, 
                textvariable=self.fit_function_title,state='readonly')
        self.fit_function_title.trace('w', self.populate_param)
        
        # number of components in fit spinbox
        self.n_component = IntVar()
        self.n_component.set(1)
        n_component_box = Spinbox(fn_select_frame,from_=1,to=20, 
                textvariable=self.n_component,width=5,command=self.populate_param)
        
        # fit button
        fit_button = ttk.Button(fn_select_frame,text='Fit',command=self.do_fit,\
                                pad=1)
        
        # set as group checkbox
        self.set_as_group = BooleanVar()
        set_group_check = ttk.Checkbutton(fn_select_frame,
                text='Set Parameters for Group',\
                variable=self.set_as_group,onvalue=True,offvalue=False)
        
        # run mode 
        fit_runmode_label_frame = ttk.Labelframe(fit_data_tab,pad=(10,5,10,5),
                text='Run Mode',)
        self.fit_runmode_label = ttk.Label(fit_runmode_label_frame,text="",
                font='bold',justify=CENTER)
        
        # fitting routine
        fit_routine_label_frame = ttk.Labelframe(fit_data_tab,pad=(10,5,10,5),
                text='Fitting Routine',)
        self.fit_routine_label = ttk.Label(fit_routine_label_frame,text="",
                font='bold',justify=CENTER)
                
        # GRIDDING
            
        # top frame gridding
        fn_select_frame_border.grid(column=0,row=0,sticky=(W,E))
        fn_select_frame.grid(column=0,row=0,sticky=(W))
        self.fit_function_title_box.grid(column=0,row=0)
        ttk.Label(fn_select_frame,text="Number of Components:").grid(column=1,
                row=0,sticky=(E),padx=5,pady=5)
        n_component_box.grid(column=2,row=0,padx=5,pady=5)
        fit_button.grid(column=3,row=0,padx=1,pady=1)
        set_group_check.grid(column=4,row=0,padx=1,pady=1)
        
        # run mode gridding
        fit_runmode_label_frame.grid(column=1,row=0,sticky=(E,W))
        self.fit_runmode_label.grid(column=0,row=0,sticky=(E,W))
        
        # routine label gridding
        fit_routine_label_frame.grid(column=2,row=0,sticky=(E,W))
        self.fit_routine_label.grid(column=0,row=0,sticky=(E,W))
        
        # MID FRAME        
        self.runbook = ttk.Notebook(mid_fit_frame)
        self.runbook.grid(column=0,row=0)
        
        # RIGHT FRAME
        
        # draw and export buttons
        button_frame = ttk.Frame(right_frame)
        draw_button = ttk.Button(button_frame,text='Draw',command=self.draw_param)
        export_button = ttk.Button(button_frame,text='Export',command=self.export)
        
        # menus for x and y values
        ttk.Label(right_frame,text="x axis:").grid(column=0,row=1)
        ttk.Label(right_frame,text="y axis:").grid(column=0,row=2)
        
        self.xaxis = StringVar()
        self.yaxis = StringVar()
        
        self.xaxis.set('')
        self.yaxis.set('')
        
        self.xaxis_combobox = ttk.Combobox(right_frame,textvariable=self.xaxis,
                                      state='readonly',width=15)
        self.yaxis_combobox = ttk.Combobox(right_frame,textvariable=self.yaxis,
                                      state='readonly',width=15)
        
        # gridding
        button_frame.grid(column=0,row=0,columnspan=2)
        draw_button.grid(column=0,row=0,padx=5,pady=5)
        export_button.grid(column=1,row=0,padx=5,pady=5)
        
        self.xaxis_combobox.grid(column=1,row=1,pady=5)
        self.yaxis_combobox.grid(column=1,row=2,pady=5)
        
        # resizing
        
        # fn select
        fn_select_frame_border.grid_columnconfigure(0,weight=1)
        fn_select_frame.grid_columnconfigure(1,weight=1)
        
        # fitting frame
        fit_data_tab.grid_rowconfigure(1,weight=1)  #fitting area
        mid_fit_frame.grid_columnconfigure(0,weight=1)
        mid_fit_frame.grid_rowconfigure(0,weight=1)
        
        # right frame
        for i in range(2):
            right_frame.grid_columnconfigure(i,weight=1)
        
    # ======================================================================= #
    def populate(self,*args):
        """
            Make tabs for setting fit input parameters. 
        """
        
        # get groups 
        dl = self.bfit.fetch_files.data_lines
        self.groups = np.unique([dl[k].group.get() for k in dl.keys()])
        
        # get run mode by looking at one of the data dictionary keys
        for key_zero in self.bfit.data.keys(): break

        # check if clearing of old tabs is needed
        keys = self.file_tabs.keys()
        do_create = not all((g in keys for g in self.groups))
        do_create = do_create or not all((g in self.groups for g in keys))
        
        # clear old tabs
        if do_create:
            for child in self.runbook.winfo_children():
                child.destroy()
        
            # reset fit function combobox options
            try:               
                if self.mode != self.bfit.data[key_zero].mode:
                    # set run mode 
                    self.mode = self.bfit.data[key_zero].mode 
                    self.fit_runmode_label['text'] = \
                            self.bfit.fetch_files.runmode_relabel[self.mode]
                    
                    # set routine
                    self.fit_routine_label['text'] = self.fitter.__name__
                    
                    # set run functions        
                    fn_titles = self.fitter.function_names[self.mode]
                    self.fit_function_title_box['values'] = fn_titles
                    self.fit_function_title.set(fn_titles[0])
                        
            except UnboundLocalError:
                self.fit_function_title_box['values'] = ()
                self.fit_function_title.set("")
                self.fit_runmode_label['text'] = ""
                self.mode = ""

                        
            # make fitinputtab objects, clean up old tabs
            for g in self.groups:
                
                # add to list of groups
                if not g in self.file_tabs.keys():
                    self.file_tabs[g] = fitinputtab(self.bfit,self.runbook,g)
                
            # clean up old tabs
            del_list = [k for k in self.file_tabs.keys() if not k in self.groups]
            
            for k in del_list:
                del self.file_tabs[k]
                        
            # add tabs to notebook
            for k in self.file_tabs.keys():
                self.file_tabs[k].create()
            
            # populate the list of parameters 
            self.populate_param()
    
        else:
            for k in self.file_tabs.keys():
                self.file_tabs[k].update()
        
    # ======================================================================= #
    def populate_param(self,*args):
        """Populate the list of parameters"""
        
        # populate tabs
        for k in self.file_tabs.keys():
            self.file_tabs[k].populate_param()
            
        # populate axis comboboxes
        lst = self.draw_components.copy()
        lst.sort()
        
        try:
            parlst = [p for p in self.fitter.gen_param_names(
                                                self.fit_function_title.get(),
                                                self.n_component.get())]
        except KeyError:
            self.xaxis_combobox['values'] = []
            self.yaxis_combobox['values'] = []
            return
            
        parlst.sort()
        
        self.xaxis_combobox['values'] = parlst+lst
        self.yaxis_combobox['values'] = parlst+lst
            
    # ======================================================================= #
    def do_fit(self,*args):
        
        # fitter
        fitter = self.fitter
        
        # get fitter inputs
        fn_name = self.fit_function_title.get()
        ncomp = self.n_component.get()
        
        # build data list
        data_list = []
        for g in self.groups:
            tab = self.file_tabs[g]
            collist = tab.collist
            runlist = tab.runlist
            
            for r in runlist:
                
                # bdata object
                bdfit = self.bfit.data[r]
                bdataobj = bdfit.bd
                
                # pdict
                pdict = {}
                for parname in tab.parentry.keys():
                    
                    # get entry values
                    pline = tab.parentry[parname]
                    line = []
                    for col in collist:
                        
                        # get number entries
                        if col in ['p0','blo','bhi']:
                            try:
                                line.append(float(pline[col][0].get()))
                            except ValueError as errmsg:
                                messagebox.showerror("Error",str(errmsg))
                        
                        # get "Fixed" entry
                        elif col in ['fixed']:
                            line.append(pline[col][0].get())
                    
                        # get "Shared" entry
                        elif col in ['shared']:
                            line.append(pline[col][0].get())
                    
                    # make dict
                    pdict[parname] = line
                    
                # doptions
                doptions = {}
                doptions['rebin'] = bdfit.rebin.get()
                doptions['group'] = bdfit.group.get()
                
                if self.mode == '1f':
                    dline = self.bfit.fetch_files.data_lines[r]
                    doptions['omit'] = dline.bin_remove.get()
                    if doptions['omit'] == dline.bin_remove_starter_line: 
                        doptions['omit'] = ''
                    
                elif self.mode == '20':
                    pass
                    
                elif self.mode == '2h':
                    pass
                    
                elif self.mode == '2e':
                    raise RuntimeError('2e fitting not implemented')
                
                else:
                    raise RuntimeError('Fitting mode not recognized')
                
                # make data list
                data_list.append([bdataobj,pdict,doptions])
        
        # call fitter with error message, potentially
        self.fit_input = (fn_name,ncomp,data_list)
        
        # make fitting status window
        fit_status_window = Toplevel(self.bfit.root)
        fit_status_window.lift()
        fit_status_window.resizable(FALSE,FALSE)
        ttk.Label(fit_status_window,text="Please Wait",pad=20).grid(column=0,
                                                    row=0,sticky=(N,S,E,W))
        fit_status_window.update_idletasks()
        self.bfit.root.update_idletasks()
        
        width = fit_status_window.winfo_reqwidth()
        height = fit_status_window.winfo_reqheight()
        
        rt_x = self.bfit.root.winfo_x()
        rt_y = self.bfit.root.winfo_y()
        rt_w = self.bfit.root.winfo_width()
        rt_h = self.bfit.root.winfo_height()
        
        x = rt_x + rt_w/2 - (width/2)
        y = rt_y + rt_h/3 - (width/2)
        
        fit_status_window.geometry('{}x{}+{}+{}'.format(width, height, int(x), int(y)))
        fit_status_window.update_idletasks()
        
        # do fit then kill window
        try:
            # fit_output keyed as {run:[key/par/cov/chi/fnpointer]}
            fit_output = fitter(fn_name=fn_name,ncomp=ncomp,
                                     data_list=data_list,
                                     hist_select=self.bfit.hist_select)
        except Exception as errmsg:
            fit_status_window.destroy()
            messagebox.showerror("Error",str(errmsg))
            raise errmsg
        else:
            fit_status_window.destroy()
        
        # set output results
        for run in fit_output.keys():
            self.bfit.data[run].set_fitresult(fit_output[run])
            
        # display run results
        for g in self.groups:
            self.file_tabs[g].set_display()
            self.file_tabs[g].set_run_color()
        
        # enable draw buttons on fetch files tab
        for r in runlist:
            self.bfit.fetch_files.data_lines[r].draw_fit_button['state'] = 'normal'
        
        # draw fit results
        self.bfit.fetch_files.draw_all(ignore_check=True)
        
        style = self.bfit.draw_style.get()
        
        if style in ['redraw','new']:
            self.bfit.draw_style.set('stack')
        
        self.bfit.fetch_files.draw_all_fits(ignore_check=True)
        self.bfit.draw_style.set(style)
            
    # ======================================================================= #
    def draw_fit(self,run,**drawargs):
        """Draw fit for a single run"""
        
        # Settings
        xlabel_dict={'20':"Time (s)",
                     '2h':"Time (s)",
                     '2e':'Frequency (MHz)',
                     '1f':'Frequency (MHz)',
                     '1n':'Voltage (V)'}
                     
        # get data and fit results
        data = self.bfit.data[run]
        fit_par = [data.fitpar['res'][p] for p in data.parnames]
        fn = data.fitfn
        data = data.bd
        
        # get draw style
        style = self.bfit.draw_style.get()
        
        # label reset
        if 'label' not in drawargs.keys():
            drawargs['label'] = self.bfit.data[run].label.get()
        drawargs['label'] += ' (fit)'
        label = drawargs['label']
        
        # set drawing style
        if style == 'new':
            plt.figure()
        if style == 'stack':
            
            ax = plt.gca()
            try:
                idx = [ell.get_label() for ell in ax.lines].index(label)
            except ValueError as err:
                pass
            else:
                del ax.lines[idx]              # clear lines 
                
        elif style == 'redraw':
            ylim = ax.get_ylim()
            xlim = ax.get_xlim()
            plt.clf()
            plt.ylim(*ylim)
            plt.xlim(*xlim)
            
        # set drawing style arguments
        for k in self.bfit.style:
            if k not in drawargs.keys() \
                    and 'marker' not in k \
                    and k not in ['elinewidth','capsize']:
                drawargs[k] = self.bfit.style[k]
        
        # linestyle reset
        if drawargs['linestyle'] == 'None': 
            drawargs['linestyle'] = '-'
        
        # draw
        t,a,da = data.asym('c')
        fitx = np.arange(self.n_fitx_pts)/float(self.n_fitx_pts)*\
                                                    (max(t)-min(t))+min(t)
        
        if   data.mode == '1f': fitxx = fitx*self.bfit.freq_unit_conv
        elif data.mode == '1n': fitxx = fitx*self.bfit.volt_unit_conv
        else:                   fitxx = fitx
    
        plt.plot(fitxx,fn(fitx,*fit_par),zorder=10,**drawargs)
        
        # plot elements
        plt.ylabel('Asymmetry')
        plt.xlabel(xlabel_dict[self.mode])
        
        # show
        plt.tight_layout()
        plt.legend()
        
    # ======================================================================= #
    def draw_param(self,*args):
        
        # make sure plot shows
        plt.ion()
        
        # get draw components
        xdraw = self.xaxis.get()
        ydraw = self.yaxis.get()
        
        # get plottable data
        try:
            xvals, xerrs = self.get_values(xdraw)
            yvals, yerrs = self.get_values(ydraw)
        except UnboundLocalError as err:
            messagebox.showerror("Error",'Select two input parameters')
            raise err
        except (KeyError,AttributeError) as err:
            messagebox.showerror("Error",
                    'Drawing parameter "%s" or "%s" not found' % (xdraw,ydraw))
            raise err
            
        # get draw style
        style = self.bfit.draw_style.get()
        
        if style == 'new':
            plt.figure()
        elif style == 'redraw':
            plt.clf()
        plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
        plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
        
        # draw
        if type(xvals[0]) == str:
            plt.xticks(np.arange(len(xvals)))
            plt.gca().set_xticklabels(xvals)
            xvals = np.arange(len(xvals))
        
        if type(yvals[0]) == str:
            plt.yticks(np.arange(len(yvals)))
            plt.gca().set_yticklabels(yvals)
            yvals = np.arange(len(yvals))
        
        plt.errorbar(xvals,yvals,xerr=xerrs,yerr=yerrs,fmt='.')
            
        # plot elements
        plt.xlabel(xdraw)
        plt.ylabel(ydraw)
        plt.tight_layout()
        
    # ======================================================================= #
    def export(self):
        
        # get values and errors
        val = {}
        for v in self.xaxis_combobox['values']:
            try:
                v2 = self.get_values(v) 
            except AttributeError: 
                traceback.print_exc()
            else:
                val[v] = v2[0]
                val['Error '+v] = v2[1]
        
        # make data frame for output
        df = pd.DataFrame(val)
        df.set_index('Run Number',inplace=True)
        
        # get file name
        filename = filedialog.asksaveasfilename()
        
        # check extension 
        if os.path.splitext(filename)[1] == '':
            filename += '.csv'
        df.to_csv(filename)
        
    # ======================================================================= #
    def get_values(self,select):
        """ Get plottable values"""
        data = self.bfit.data
        runs = list(data.keys())
        runs.sort()
    
        # Data file options
        if select == 'Temperature (K)':
            val = [data[r].temperature.mean for r in runs]
            err = [data[r].temperature.std for r in runs]
        
        elif select == 'B0 Field (T)':
            val = [data[r].field for r in runs]
            err = [data[r].field_std for r in runs]
        
        elif select == 'RF Level DAC':
            val = [data[r].camp.rf_dac.mean for r in runs]
            err = [data[r].camp.rf_dac.std for r in runs]
        
        elif select == 'Platform Bias (kV)':
            try:
                val = [data[r].bias for r in runs]
                err = [data[r].bias_std for r in runs]
            except AttributeError:
                pass
                
        elif select == 'Impl. Energy (keV)':
            val =  [data[r].bd.beam_kev() for r in runs]
            err =  [0 for r in runs]
        
        elif select == 'Run Duration (s)':
            val = [data[r].bd.duration for r in runs]
            err = [0 for r in runs]
        
        elif select == 'Run Number':
            val = [data[r].run for r in runs]
            err = [0 for r in runs]
        
        elif select == 'Sample':
            val = [data[r].bd.sample for r in runs]
            err = [0 for r in runs]
            
        elif select == 'Start Time':
            val = [data[r].bd.start_date for r in runs]
            err = [0 for r in runs]
        
        # fitted parameter options
        elif select in self.fitter.gen_param_names(self.fit_function_title.get(),
                                                   self.n_component.get()):
            val = []
            err = []
            
            for r in runs:
                try:
                    val.append(self.bfit.data[r].fitpar['res'][select])
                    err.append(self.bfit.data[r].fitpar['dres'][select])
                except KeyError:
                    val.append(np.nan)
                    err.append(np.nan)
    
        return (val,err)
    
# =========================================================================== #
# =========================================================================== #
class fitinputtab(object):
    """
        Instance variables 
        
            bfit        pointer to top class
            data        pointer to bfit.data
            parent      pointer to parent object (frame)
            group       fitting group number
            parlabels   label objects, saved for later destruction
            parentry    [parname][colname] of ttk.Entry objects saved for 
                            retrieval and destruction
            runbox      listbox with run numbers: select which result to display
            run_label   label for showing which run is selected
            runlist     list of run numbers to fit
            selected    index of selected run in runbox (int)
            fitframe    mainframe for this tab. 
    """
    
    n_runs_max = 5      # number of runs before scrollbar appears
    collist = ['p0','blo','bhi','res','dres','chi','fixed','shared']
    selected = 0        # index of selected run 
    
    # ======================================================================= #
    def __init__(self,bfit,parent,group):
        """
            Inputs:
                bfit: top level pointer
                parent      pointer to parent object (frame)
                group: number of data group to fit
        """
        
        # initialize
        self.bfit = bfit
        self.parent = parent
        self.group = group
        self.parlabels = []
        self.parentry = {}
        
    # ======================================================================= #
    def create(self):
        """Create graphics for this object"""
        
        fitframe = ttk.Frame(self.parent)
        self.parent.add(fitframe,text='Group %d' % self.group)
        
        # get list of runs with the group number
        dl = self.bfit.fetch_files.data_lines
        self.runlist = [dl[k].run for k in dl.keys() 
                if dl[k].group.get() == self.group]
        
        # Display run info label 
        ttk.Label(fitframe,text="Run Numbers").grid(column=0,row=1,padx=5)

        # List box for run viewing
        rlist = StringVar(value=tuple(map(str,self.runlist)))
        self.runbox = Listbox(fitframe,height=min(len(self.runlist),self.n_runs_max),
                                width=10,listvariable=rlist,justify=CENTER,
                                selectmode=BROWSE)
        self.runbox.activate(0)
        self.runbox.bind('<<ListboxSelect>>',self.set_display)
        self.runbox.grid(column=0,row=2,rowspan=self.n_runs_max)
        
        sbar = ttk.Scrollbar(fitframe,orient=VERTICAL,command=self.runbox.yview)
        self.runbox.configure(yscrollcommand=sbar.set)
        
        if len(self.runlist) > self.n_runs_max:
            sbar.grid(column=1,row=2,sticky=(N,S),rowspan=self.n_runs_max)
        else:
            ttk.Label(fitframe,text=" ").grid(column=1,row=2,padx=5)
        
        # label for displyaing run number
        self.run_label = ttk.Label(fitframe,text='',font='bold')
        
        # Parameter input labels
        c = 2
        ttk.Label(fitframe,text='Parameter').grid(      column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Initial Value').grid(  column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Low Bound').grid(      column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='High Bound').grid(     column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Result').grid(         column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Result Error').grid(   column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='ChiSq').grid(          column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Fixed').grid(          column=c,row=1,padx=5); c+=1
        ttk.Label(fitframe,text='Shared').grid(         column=c,row=1,padx=5); c+=1
        
        # grid the run_label
        self.run_label.grid(column=0,row=0,padx=5,pady=5,columnspan=c-1)
        
        # resizing
        for i in (4,5):
            fitframe.grid_columnconfigure(i,weight=1000)      # bounds
        for i in (1,2,3):
            fitframe.grid_columnconfigure(c-i,weight=10)  # fixed,share,chi
        
        fitframe.grid_columnconfigure(0,weight=1)           # run select
        
        fitframe.grid_rowconfigure(0,weight=1)              # run title
        
        for i in range(2,50):
            fitframe.grid_rowconfigure(i,weight=1)
        self.parent.grid_rowconfigure(1,weight=1)
        
        # save
        self.fitframe = fitframe
        
    # ======================================================================= #
    def get_new_parameters(self,runlist):
        """
            Fetch initial parameters from fitter, set to data.    
            
            runlist: list of run numbers to set new parameters for. 
        """
        
        # get pointer to fit files object
        fit_files = self.bfit.fit_files
        fitter = fit_files.fitter
        ncomp = fit_files.n_component.get()
        fn_title = fit_files.fit_function_title.get()
        
        # get list of parameter names
        plist = fitter.gen_param_names(fn_title,ncomp)
        for run in runlist:
            
            # get init values
            values = fitter.gen_init_par(fn_title,ncomp,self.bfit.data[run].bd)
            
            # set to data
            self.bfit.data[run].set_fitpar(values)
        
        return plist
        
    # ======================================================================= #
    def get_selected_run(self):
        """Get the run number of the selected run"""
        
        try:
            self.selected = self.runbox.curselection()[0]
        except IndexError:
            self.selected = 0 
            
        return self.runlist[self.selected]
        
    # ======================================================================= #
    def populate_param(self):
        """Populate the list of parameters"""
        
        # get list of parameters and initial values
        try:
            plist = self.get_new_parameters(self.runlist)
        except KeyError:
            return
        finally:
            for label in self.parlabels:
                label.destroy()
            for k in self.parentry.keys():
                for p in self.parentry[k]:
                    self.parentry[k][p][1].destroy()
        
        
        # make parameter input fields ---------------------------------------
        
        # labels
        c = 2
        
        self.parlabels = []     # track all labels and inputs
        for i,p in enumerate(plist):
            self.parlabels.append(ttk.Label(self.fitframe,text=p,justify=LEFT))
            self.parlabels[-1].grid(column=c,row=2+i,padx=5,sticky=E)
        
        # get data of selected run
        run = self.get_selected_run()
        fitdat = self.bfit.data[run]
        
        # input values: initial parameters
        r = 1
        for p in plist:         # iterate parameter names
            c = 2   # gridding column         
            r += 1  # gridding row         
            self.parentry[p] = {}
            for i in range(3):
                c += 1
                
                value = StringVar()
                entry = ttk.Entry(self.fitframe,textvariable=value,width=10)
                entry.insert(0,str(fitdat.fitpar[self.collist[i]][p]))
                entry.grid(column=c,row=r,padx=5,sticky=E)
                self.parentry[p][self.collist[i]] = (value,entry)
            
            # do results
            c += 1
            par_val = StringVar()
            par = ttk.Entry(self.fitframe,textvariable=par_val,width=15)
            par['state'] = 'readonly'
            par['foreground'] = 'black'
            
            dpar_val = StringVar()
            dpar = ttk.Entry(self.fitframe,textvariable=dpar_val,width=10)
            dpar['state'] = 'readonly'
            dpar['foreground'] = 'black'
                                     
            par. grid(column=c,row=r,padx=5,sticky=E); c += 1
            dpar.grid(column=c,row=r,padx=5,sticky=E); c += 1

            # do chi only once
            if r == 2:
                chi_val = StringVar()
                chi = ttk.Entry(self.fitframe,textvariable=chi_val,width=7)
                chi['state'] = 'readonly'
                chi['foreground'] = 'black'
                
                chi.grid(column=c,row=r,padx=5,sticky=E,rowspan=len(plist)); 
            c += 1
            
            # save ttk.Entry objects in dictionary [parname][colname]
            self.parentry[p][self.collist[3]] = (par_val,par)
            self.parentry[p][self.collist[4]] = (dpar_val,dpar)
            self.parentry[p][self.collist[5]] = (chi_val,chi)
            
            # do fixed box
            value = BooleanVar()
            entry = ttk.Checkbutton(self.fitframe,text='',\
                                     variable=value,onvalue=True,offvalue=False)
            entry.grid(column=c,row=r,padx=5,sticky=E); c += 1
            self.parentry[p][self.collist[6]] = (value,entry)
            
            # do shared box
            value = BooleanVar()
            entry = ttk.Checkbutton(self.fitframe,text='',\
                                     variable=value,onvalue=True,offvalue=False)
            entry.grid(column=c,row=r,padx=5,sticky=E); c += 1
            self.parentry[p][self.collist[7]] = (value,entry)
        
        # set parameters
        self.set_display()
        
    # ======================================================================= #
    def set_display(self,*args):
        """Set initial parameters and fit results in display to that of selected run"""
        
        # INITIAL PARAMETERS
        
        # get data that is currently there, possibly for whole group
        run = self.runlist[self.selected]
        fitdat_old = self.bfit.data[run]
        
        # set as group 
        if self.bfit.fit_files.set_as_group.get():
            fitdat_list = [self.bfit.data[r] for r in self.runlist]
        else:
            fitdat_list = [fitdat_old]
        
        # get run number of new selected run
        run = self.get_selected_run()
        fitdat_new = self.bfit.data[run]
    
        # set label for run slection 
        self.run_label['text'] = '[ %d ]' % (run)
    
        for p in self.parentry.keys():  # parentry = [parname][colname][value,entry]
            for i in range(3):          # iterate input columns
                col = self.collist[i]   # column title
        
                # get new initial parameter
                if len(fitdat_new.fitpar[col].keys()) == 0:
                    self.get_new_parameters([run])
                newpar = float(self.parentry[p][col][0].get())
                    
                # check data of old entry: True if change data of all runs
                change_par = fitdat_old.fitpar[col][p] != newpar
                
                # set parameters of all data
                if change_par: 
                    for d in fitdat_list:
                        d.fitpar[col][p] = newpar
                
                # set only selected run
                else:
                    fitdat_old.fitpar[col][p] = newpar
                    
                # set values of new data
                self.parentry[p][col][0].set(
                            ("%"+".%df" % self.bfit.rounding) % \
                            fitdat_new.fitpar[col][p])
                
            # get fixed status of old data then set to new
            try:
                newpar = self.parentry[p]['fixed'][0].get()
                change_par = fitdat_old.fitpar['fixed'][p] != newpar
            except KeyError:
                pass
            else:
                if change_par:
                    for d in fitdat_list:   
                        d.fitpar['fixed'][p] = newpar
                else:
                    fitdat_old.fitpar['fixed'][p] = newpar
            
            try:
                self.parentry[p]['fixed'][0].set(fitdat_new.fitpar['fixed'][p])
            except KeyError:
                fitdat_new.fitpar['fixed'][p] = False
                self.parentry[p]['fixed'][0].set(False)
    
            # get and set shared status 
            try:
                newpar = self.parentry[p]['shared'][0].get()
                change_par = fitdat_old.fitpar['shared'][p] != newpar
            except KeyError:
                pass
            else:
                if change_par:
                    for d in [self.bfit.data[r] for r in self.runlist]:   # shared is always shared
                        d.fitpar['shared'][p] = newpar
                else:
                    fitdat_old.fitpar['shared'][p] = newpar
            
            try:
                self.parentry[p]['shared'][0].set(fitdat_new.fitpar['shared'][p])
            except KeyError:
                fitdat_new.fitpar['shared'][p] = False
                self.parentry[p]['shared'][0].set(False)
            
        # FIT RESULTS    
        
        # Set up variables
        displays = self.parentry
        
        # get run number of selected run
        run = self.get_selected_run()
        
        try:
            data = self.bfit.data[run]
        except KeyError:
            return
            
        try:
            chi = data.chi
        except AttributeError:
            return 
        
        # display
        for parname in data.fitpar['res'].keys():
            disp = displays[parname]
            showstr = "%"+".%df" % self.bfit.rounding
            disp['res'][0].set(showstr % data.fitpar['res'][parname])
            disp['dres'][0].set(showstr % data.fitpar['dres'][parname])
            disp['chi'][0].set(showstr % chi)
         
    # ======================================================================= #
    def set_run_color(self):
        """On fit, set the color of the line in the run number select."""

        runlist = map(int,self.runbox.get(0,self.runbox.size()))
        
        for i,r in enumerate(runlist):
            if self.bfit.data[r].chi > self.bfit.fit_files.chi_threshold:
                self.runbox.itemconfig(i, {'bg':'red'})
            else:
                self.runbox.itemconfig(i, {'bg':'white'})

    # ======================================================================= #
    def update(self):
        """Update tab with new data"""
        
        # get list of runs with the group number
        dl = self.bfit.fetch_files.data_lines
        self.runlist = [dl[k].run for k in dl.keys() 
                if dl[k].group.get() == self.group]
        
        # List box for run viewing
        rlist = StringVar(value=tuple(map(str,self.runlist)))
        self.runbox.config(height=min(len(self.runlist),self.n_runs_max))
        self.runbox.config(listvariable=rlist)
        self.runbox.activate(0)
        
        
        
        
        
