# fit_files tab for bfit
# Derek Fujimoto
# Dec 2017

from tkinter import *
from tkinter import ttk, messagebox, filedialog
import numpy as np
import pandas as pd
from functools import partial
from bdata import bdata
import datetime
import matplotlib.pyplot as plt

# =========================================================================== #
# =========================================================================== #
class fit_files(object):
    """
        Data fields:
            data: dictionary of bdata objects, keyed by run number. 
            file_tabs: dictionary of fitinputtab objects, keyed by runnumber 
            fitter: fitting object from self.bfit.routine_mod
            fit_function_title: title of fit function to use
            fit_function_title_box: spinbox for fit function names
            fit_input:  fitting input values = (fn_name,ncomp,data_list)
            fit_output: fitting results, output of fitter
            groups: group numbers from fetch tab
            n_component: number of fitting components
            runbook: notebook of fit inputs for runs
            runmode: what type of run is this. 
            runmode_label: display run mode 
            xaxis: StringVar() for parameter to draw on x axis
            yaxis: StringVar() for parameter to draw on y axis
            xaxis_combobox: box for choosing x axis draw parameter
            yaxis_combobox: box for choosing y axis draw parameter
    """ 
    
    runmode_relabel = {'20':'SLR','1f':'1F','2e':'2e','1n':'Rb Cell Scan'}
    default_fit_functions = {'20':('Exp','Str Exp'),
            '1f':('Lorentzian','Gaussian'),'1n':('Lorentzian','Gaussian')}
    mode = ""

    # define draw componeents in draw_param
    draw_components = ['Temperature','B0 Field', 'RF Level DAC', 'Platform Bias', 
                       'Beam Energy', 'Run Duration','Run Number','Sample', 
                       'Start Time']

    # ======================================================================= #
    def __init__(self,fit_data_tab,bfit):
        
        # Key binding
        #~ fit_data_tab.bind('<FocusIn>',self.populate)   ################################ REBIND!
        
        # initialize
        self.file_tabs = {}
        self.bfit = bfit
        self.groups = []
        self.fit_output = {}
        self.fitter = self.bfit.routine_mod.fitter()
            
        # make top level frames
        top_fit_frame = ttk.Frame(fit_data_tab,pad=5)   # fn select, run mode
        mid_fit_frame = ttk.Frame(fit_data_tab,pad=5)   # notebook
        right_frame = ttk.Labelframe(fit_data_tab,text='Fit Results',pad=5)     # draw fit results
        
        top_fit_frame.grid(column=0,row=0,sticky=(N,W))
        mid_fit_frame.grid(column=0,row=1,sticky=(N,W))
        right_frame.grid(column=1,row=1,columnspan=2,rowspan=2,sticky=(N,W,E))
        
        # TOP FRAME 
        
        # fit function select 
        fn_select_frame = ttk.Labelframe(fit_data_tab,text='Fit Function')
        self.fit_function_title = StringVar()
        self.fit_function_title.set("")
        self.fit_function_title_box = ttk.Combobox(fn_select_frame, 
                textvariable=self.fit_function_title,state='readonly')
        self.fit_function_title.trace('w', self.populate_param)
        
        # number of components in fit spinbox
        self.n_component = IntVar()
        self.n_component.set(1)
        n_component_box = Spinbox(fn_select_frame,from_=1,to=20, 
                textvariable=self.n_component,width=5)
        
        # fit button
        fit_button = ttk.Button(fn_select_frame,text='Fit',command=self.do_fit,\
                                pad=1)
        
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
        fn_select_frame.grid(column=0,row=0,sticky=(E,W))
        self.fit_function_title_box.grid(column=0,row=0)
        ttk.Label(fn_select_frame,text="Number of Components:").grid(column=1,
                row=0,sticky=(E),padx=5,pady=5)
        n_component_box.grid(column=2,row=0,padx=5,pady=5)
        fit_button.grid(column=3,row=0,padx=1,pady=1)
        
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
        draw_button = ttk.Button(right_frame,text='Draw',command=self.draw_param)
        export_button = ttk.Button(right_frame,text='Export',command=self.export_param)
        
        #~ draw_button.bind('<Return>',self.draw_param)   ################################ REBIND!
        
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
        draw_button.grid(column=0,row=0,padx=5,pady=5)
        export_button.grid(column=1,row=0,padx=5,pady=5)
        
        self.xaxis_combobox.grid(column=1,row=1,pady=5)
        self.yaxis_combobox.grid(column=1,row=2,pady=5)
        
    # ======================================================================= #
    def populate(self,*args):
        """
            Make tabs for setting fit input parameters. 
        """
        
        # get data
        self.data = self.bfit.fetch_files.data
        
        # get groups 
        dl = self.bfit.fetch_files.data_lines
        self.groups = [dl[k].group.get() for k in dl.keys()]
        
        # get run mode by looking at one of the data dictionary keys
        for key_zero in self.data.keys(): break
        
        # reset fit function combobox options
        try:                
            # set run mode 
            self.mode = self.data[key_zero].mode 
            self.fit_runmode_label['text'] = self.runmode_relabel[self.mode]
            
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
        
        # clear old tabs
        for child in self.runbook.winfo_children():
            child.destroy()
        
        # make fitinputtab objects, clean up old tabs
        del_list = []
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
            parlst = [p for p in self.fitter.param_names[self.fit_function_title.get()]]
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
            runlist = tab.runlist
            
            
            for r in runlist:
                
                # bdata object
                bdataobj = self.bfit.fetch_files.data[r]
                
                # pdict
                pdict = {}
                for parname in tab.parentry.keys():
                    
                    # get entry values
                    pline = tab.parentry[parname]
                    line = []
                    for i,p in enumerate(pline):
                        
                        # get number entries
                        if i < 3:
                            try:
                                line.append(float(p[0].get()))
                            except ValueError as errmsg:
                                messagebox.showerror("Error",str(errmsg))
                        
                        # get "Fixed" entry
                        else:
                            line.append(p[0].get())
                    
                    # make dict
                    pdict[parname] = line
                    
                # doptions
                doptions = {}
                doptions['rebin'] = self.bfit.fetch_files.data_lines[r].rebin.get()
                doptions['group'] = g
                
                if self.mode == '1f':
                    doptions['omit'] = self.bfit.fetch_files.data_lines[r].bin_remove.get()
                    
                elif self.mode == '20':
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
        ttk.Label(fit_status_window,text="Please Wait",pad=5).grid(column=0,
                                                    row=0,sticky=(N,S,E,W))
        fit_status_window.update_idletasks()
        width = fit_status_window.winfo_reqwidth()
        height = fit_status_window.winfo_reqheight()
        x = (self.bfit.root.winfo_screenwidth() / 2) - (width / 2)
        y = (fit_status_window.winfo_screenheight() / 3) - (height / 2)
        fit_status_window.geometry('{}x{}+{}+{}'.format(width, height, int(x), int(y)))
        fit_status_window.update_idletasks()
        
        # do fit then kill window
        try:
            self.fit_output = fitter(fn_name=fn_name,ncomp=ncomp,data_list=data_list)
        except Exception as errmsg:
            print(errmsg)
            fit_status_window.destroy()
            messagebox.showerror("Error",str(errmsg))
        else:
            fit_status_window.destroy()
        
    #======================================================================== #
    def draw_fits(self,*args):
        
        data = self.data
        fit_out = self.fit_output
        fit
        
        # condense drawing into a funtion
        def draw_single():
            # draw the thing here #######################################################################
            pass
                
        # get draw style
        style = self.bfit.draw_style.get()
        
        # make new figure, draw stacked
        if style == 'stack':
            plt.figure()
            draw_single()
            
        # overdraw in current figure, stacked
        elif style == 'redraw':
            plt.clf()
            self.bfit.draw_style.set('stack')
            draw_single()
            self.bfit.draw_style.set('redraw')
            
        # make new figure, draw single
        elif style == 'new':
            draw_single()
        else:
            raise ValueError("Draw style not recognized")
        
    # ======================================================================= #
    def draw_param(self,*args):
        
        # make sure plot shows
        plt.ion()
        
        # get draw components
        xdraw = self.xaxis.get()
        ydraw = self.yaxis.get()
        
        # get data dictionary
        data = self.data
        runs = list(data.keys())
        
        # output parameters 
        parout = self.fit_output
        
        # get values to draw
        def get_values(select):
            
            # Data file options
            if select == 'Temperature':
                val = [data[r].camp.smpl_read_A.mean for r in runs]
                err = [data[r].camp.smpl_read_A.std for r in runs]
            
            elif select == 'B0 Field':
                val = [data[r].camp.b_field.mean for r in runs]
                err = [data[r].camp.b_field.std for r in runs]
            
            elif select == 'RF Level DAC':
                val = [data[r].camp.rf_dac.mean for r in runs]
                err = [data[r].camp.rf_dac.std for r in runs]
            
            elif select == 'Platform Bias':
                val = [data[r].epics.nmr_bias_p.mean for r in runs]
                err = [data[r].epics.nmr_bias_p.std for r in runs]
            
            elif select == 'Beam Energy':
                val =  [data[r].beam_kev() for r in runs]
                err =  [0 for r in runs]
            
            elif select == 'Run Duration':
                val = [data[r].duration for r in runs]
                err = [0 for r in runs]
            
            elif select == 'Run Number':
                val = [data[r].run for r in runs]
                err = [0 for r in runs]
            
            elif select == 'Sample':
                val = [data[r].sample for r in runs]
                err = [0 for r in runs]
                
            elif select == 'Start Time':
                val = [data[r].start_date for r in runs]
                err = [0 for r in runs]
            
            # fitted parameter options
            elif select in self.fitter.param_names[self.fit_function_title.get()]:
                val = [parout[r][1][parout[r][0].index(select)] for r in runs]
                err = [parout[r][2][parout[r][0].index(select)] for r in runs]
            
            return (val,err)
        
        # get plottable data
        try:
            xvals, xerrs = get_values(xdraw)
            yvals, yerrs = get_values(ydraw)
        except UnboundLocalError:
            messagebox.showerror("Error",'Select two input parameters')
            return
        except KeyError:
            messagebox.showerror("Error",'Refit data')
            return
            
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
    def export_param(self):
        pass
        
# =========================================================================== #
# =========================================================================== #
class fitinputtab(object):
    """
        Instance variables 
        
            bfit        pointer to top class
            parent      pointer to parent object (frame)
            group       fitting group number
            parlabels   label objects, saved for later destruction
            parentry    {parname:(StrVar,entry)} objects saved for retrieval and destruction
            runlist     list of run numbers to fit
            fitframe    mainframe for this tab. 
    """
    
    
    
    n_runs_max = 5      # number of runs before scrollbar appears
    
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
        ttk.Label(fitframe,text="Run Numbers").grid(column=0,row=0,padx=5)

        # List box for run viewing
        rlist = StringVar(value=tuple(map(str,self.runlist)))
        runbox = Listbox(fitframe,height=min(len(self.runlist),self.n_runs_max),
                         width=10,listvariable=rlist,justify=CENTER)
        runbox.grid(column=0,row=1,rowspan=10)
        
        sbar = ttk.Scrollbar(fitframe, orient=VERTICAL, command=runbox.yview)
        runbox.configure(yscrollcommand=sbar.set)
        
        if len(self.runlist) > self.n_runs_max:
            sbar.grid(column=1,row=1,sticky=(N,S),rowspan=10)
        else:
            ttk.Label(fitframe,text=" ").grid(column=1,row=1,padx=5)
        
        # Parameter input labels
        c = 2
        ttk.Label(fitframe,text='Parameter').grid(      column=c,row=0,padx=5); c+=1
        ttk.Label(fitframe,text='Initial Value').grid(  column=c,row=0,padx=5); c+=1
        ttk.Label(fitframe,text='Low Bound').grid(      column=c,row=0,padx=5); c+=1
        ttk.Label(fitframe,text='High Bound').grid(     column=c,row=0,padx=5); c+=1
        ttk.Label(fitframe,text='Fixed').grid(          column=c,row=0,padx=5); c+=1
        
        # save
        self.fitframe = fitframe
        
    # ======================================================================= #
    def populate_param(self):
        """Populate the list of parameters"""

        # get pointer to fit files object
        fit_files = self.bfit.fit_files
        fitter = fit_files.fitter

        # get list of parameters and initial values
        try:
            plist = fitter.param_names[fit_files.fit_function_title.get()]
            values = fitter.gen_init_par(fit_files.fit_function_title.get())
        except KeyError:
            return
        finally:
            # clear old entries
            for label in self.parlabels:
                label.destroy()
            for k in self.parentry.keys():
                for p in self.parentry[k]:
                    p[1].destroy()
        
        # make parameter input fields ---------------------------------------
        
        # labels
        c = 2
        
        self.parlabels = []     # track all labels and inputs
        for i,p in enumerate(plist):
            self.parlabels.append(ttk.Label(self.fitframe,text=p,justify=LEFT))
            self.parlabels[-1].grid(column=c,row=1+i,padx=5,sticky=E)
        
        # values: initial parameters
        r = 0
        for p in plist:
            c = 2
            r += 1
            self.parentry[p] = []
            for i in range(len(values[list(values.keys())[0]])-1):
                c += 1
                value = StringVar()
                entry = ttk.Entry(self.fitframe,textvariable=value,width=10)
                entry.insert(0,str(values[p][i]))
                entry.grid(column=c,row=r,padx=5,sticky=E)
                self.parentry[p].append((value,entry))
            
            # do fixed box
            c += 1
            value = BooleanVar()
            entry = ttk.Checkbutton(self.fitframe,text='',\
                                     variable=value,onvalue=True,offvalue=False)
            entry.grid(column=c,row=r,padx=5,sticky=E)
            self.parentry[p].append((value,entry))
            
        
