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
            chi_threshold: if chi > thres, set color to red
            data: dictionary of bdata objects, keyed by run number. 
            file_tabs: dictionary of fitinputtab objects, keyed by group number 
            fitter: fitting object from self.bfit.routine_mod
            fit_function_title: title of fit function to use
            fit_function_title_box: spinbox for fit function names
            fit_input:  fitting input values = (fn_name,ncomp,data_list)
            fit_output: fitting results, output of fitter
            groups: group numbers from fetch tab
            mode: what type of run is this. 
            n_component: number of fitting components (IntVar)
            runbook: notebook of fit inputs for runs
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
    chi_threshold = 1.5 # threshold for red highlight on bad fits 
    n_fitx_pts = 500    # number of points to draw in fitted curves

    # define draw componeents in draw_param
    draw_components = ['Temperature (K)','B0 Field (T)', 'RF Level DAC', 
                       'Platform Bias (kV)', 'Impl. Energy (keV)', 
                       'Run Duration (s)', 'Run Number','Sample', 'Start Time']

    # ======================================================================= #
    def __init__(self,fit_data_tab,bfit):
        
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
                textvariable=self.n_component,width=5,command=self.populate_param)
        
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
        button_frame = ttk.Frame(right_frame)
        draw_button = ttk.Button(button_frame,text='Draw',command=self.draw_param)
        export_button = ttk.Button(button_frame,text='Export',command=self.export)
        
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
        button_frame.grid(column=0,row=0,columnspan=2)
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
                bdataobj = self.bfit.fetch_files.data[r]
                
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
                    
                    # make dict
                    pdict[parname] = line
                    
                # doptions
                doptions = {}
                doptions['rebin'] = self.bfit.fetch_files.data_lines[r].rebin.get()
                doptions['group'] = g
                
                if self.mode == '1f':
                    dline = self.bfit.fetch_files.data_lines[r]
                    doptions['omit'] = dline.bin_remove.get()
                    if doptions['omit'] == dline.bin_remove_starter_line: 
                        doptions['omit'] = ''
                    
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
            self.fit_output = fitter(fn_name=fn_name,ncomp=ncomp,
                                     data_list=data_list,
                                     hist_select=self.bfit.hist_select)
        except Exception as errmsg:
            fit_status_window.destroy()
            messagebox.showerror("Error",str(errmsg))
            raise errmsg
        else:
            fit_status_window.destroy()
        
        # display run results
        for g in self.groups:
            self.file_tabs[g].set_fit_results()
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
        data = self.data[run]
        fit_out = self.fit_output[run]
        fn = self.fitter.fn_list[run]
                
        # get draw style
        style = self.bfit.draw_style.get()
        
        # set drawing style
        if style == 'new':
            plt.figure()
        elif style == 'redraw':
            plt.clf()
            
        # set drawing style arguments
        for k in self.bfit.style:
            if k not in drawargs.keys() \
                    and 'marker' not in k \
                    and k not in ['elinewidth','capsize']:
                drawargs[k] = self.bfit.style[k]
        
        # linestyle reset
        if drawargs['linestyle'] == 'None': 
            drawargs['linestyle'] = '-'
        
        # label reset
        if 'label' not in drawargs.keys():
            drawargs['label'] = self.bfit.fetch_files.data_lines[run].label.get()
        
        # draw
        t,a,da = data.asym('c')
        fitx = np.arange(self.n_fitx_pts)/float(self.n_fitx_pts)*\
                                                    (max(t)-min(t))+min(t)
        
        if   data.mode == '1f': fitxx = fitx*self.bfit.freq_unit_conv
        elif data.mode == '1n': fitxx = fitx*self.bfit.volt_unit_conv
        else:                   fitxx = fitx
    
        plt.plot(fitxx,fn(fitx,*(fit_out[1])),zorder=10,**drawargs)
        
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
        data = self.data
        runs = list(data.keys())
        runs.sort()
        parout = self.fit_output
    
        # Data file options
        if select == 'Temperature (K)':
            val = [data[r].camp.smpl_read_A.mean for r in runs]
            err = [data[r].camp.smpl_read_A.std for r in runs]
        
        elif select == 'B0 Field (T)':
            try:
                val = [data[r].camp.b_field.mean for r in runs]
                err = [data[r].camp.b_field.std for r in runs]
            except AttributeError:
                val = [current2field(data[r].epics.hh_current.mean)/1e4 for r in runs]
                err = [current2field(data[r].epics.hh_current.std)/1e4 for r in runs]
        
        elif select == 'RF Level DAC':
            val = [data[r].camp.rf_dac.mean for r in runs]
            err = [data[r].camp.rf_dac.std for r in runs]
        
        elif select == 'Platform Bias (kV)':
            try:
                val = [data[r].epics.nmr_bias.mean for r in runs]
                err = [data[r].epics.nmr_bias.std for r in runs]
            except AttributeError:
                val = [data[r].epics.nqr_bias.mean/1000. for r in runs]
                err = [data[r].epics.nqr_bias.std/1000. for r in runs]
                
        elif select == 'Impl. Energy (keV)':
            val =  [data[r].beam_kev() for r in runs]
            err =  [0 for r in runs]
        
        elif select == 'Run Duration (s)':
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
        elif select in self.fitter.gen_param_names(self.fit_function_title.get(),
                                                   self.n_component.get()):
            val = []
            err = []
            
            for r in runs:
                try:
                    val.append(parout[r][1][parout[r][0].index(select)])
                    err.append(parout[r][2][parout[r][0].index(select)])
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
            parent      pointer to parent object (frame)
            group       fitting group number
            parlabels   label objects, saved for later destruction
            parentry    {parname:(StrVar,entry)} objects saved for retrieval and destruction
            runbox      listbox with run numbers: select which result to display
            runlist     list of run numbers to fit
            fitframe    mainframe for this tab. 
    """
    
    n_runs_max = 5      # number of runs before scrollbar appears
    collist = ['p0','blo','bhi','res','dres','chi','fixed']
    
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
        self.runbox = Listbox(fitframe,height=min(len(self.runlist),self.n_runs_max),
                         width=10,listvariable=rlist,justify=CENTER,
                        selectmode=BROWSE)
        self.runbox.activate(0)
        self.runbox.bind('<<ListboxSelect>>',self.set_fit_results)
        self.runbox.grid(column=0,row=1,rowspan=10)
        
        sbar = ttk.Scrollbar(fitframe,orient=VERTICAL,command=self.runbox.yview)
        self.runbox.configure(yscrollcommand=sbar.set)
        
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
        ttk.Label(fitframe,text='Result').grid(         column=c,row=0,padx=5); c+=1
        ttk.Label(fitframe,text='Result Error').grid(   column=c,row=0,padx=5); c+=1
        ttk.Label(fitframe,text='ChiSq').grid(          column=c,row=0,padx=5); c+=1
        ttk.Label(fitframe,text='Fixed').grid(          column=c,row=0,padx=5); c+=1
        
        # save
        self.fitframe = fitframe
        
    # ======================================================================= #
    def populate_param(self):
        """Populate the list of parameters"""

        # get pointer to fit files object
        fit_files = self.bfit.fit_files
        fitter = fit_files.fitter
        ncomp = fit_files.n_component.get()
        fn_title = fit_files.fit_function_title.get()

        # get list of parameters and initial values
        try:
            plist = fitter.gen_param_names(fn_title,ncomp)
            values = fitter.gen_init_par(fn_title,ncomp)
        except KeyError:
            return
        finally:
            # clear old entries
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
            self.parlabels[-1].grid(column=c,row=1+i,padx=5,sticky=E)
        
        # values: initial parameters
        r = 0
        for p in plist:
            c = 2
            r += 1
            self.parentry[p] = {}
            for i in range(3):
                c += 1
                value = StringVar()
                entry = ttk.Entry(self.fitframe,textvariable=value,width=10)
                entry.insert(0,str(values[p][i]))
                entry.grid(column=c,row=r,padx=5,sticky=E)
                self.parentry[p][self.collist[i]] = (value,entry)
            
            # do results
            c += 1
            value_p = StringVar()
            par = ttk.Entry(self.fitframe,textvariable=value_p,width=10)
            par['state'] = 'readonly'
            par['foreground'] = 'black'
            
            value_dp = StringVar()
            dpar = ttk.Entry(self.fitframe,textvariable=value_dp,width=10)
            dpar['state'] = 'readonly'
            dpar['foreground'] = 'black'
            
            value_chi = StringVar()
            chi = ttk.Entry(self.fitframe,textvariable=value_chi,width=10)
            chi['state'] = 'readonly'
            chi['foreground'] = 'black'
                                     
            par. grid(column=c,row=r,padx=5,sticky=E); c += 1
            dpar.grid(column=c,row=r,padx=5,sticky=E); c += 1
            chi. grid(column=c,row=r,padx=5,sticky=E); c += 1
            
            self.parentry[p][self.collist[3]] = (value_p,par)
            self.parentry[p][self.collist[4]] = (value_dp,dpar)
            self.parentry[p][self.collist[5]] = (value_chi,chi)
            
            # do fixed box
            value = BooleanVar()
            entry = ttk.Checkbutton(self.fitframe,text='',\
                                     variable=value,onvalue=True,offvalue=False)
            entry.grid(column=c,row=r,padx=5,sticky=E)
            self.parentry[p][self.collist[6]] = (value,entry)
            
    # ======================================================================= #
    def set_fit_results(self,*args):
        """Show fit results"""
        
        # Set up variables
        out = self.bfit.fit_files.fit_output
        displays = self.parentry
        
        # get run number of selected run
        try:
            line = self.runbox.curselection()[0]
        except IndexError:
            line = 0 
            self.runbox.select_set(0)
            self.runbox.event_generate("<<ListboxSelect>>")
        run = self.runlist[line]
        out = out[run]
        chi = out[3]
        
        # display
        for name,val,err in zip(*(out[:3])):
            disp = displays[name]
            showstr = "%"+".%dg" % self.bfit.rounding
            disp['res'][0].set(showstr % val)
            disp['dres'][0].set(showstr % err)
            disp['chi'][0].set(showstr % chi)
         
    # ======================================================================= #
    def set_run_color(self):
        """On fit, set the color of the line in the run number select."""

        runlist = map(int,self.runbox.get(0,self.runbox.size()))
        out = self.bfit.fit_files.fit_output
        
        for i,r in enumerate(runlist):
            if out[r][3] > self.bfit.fit_files.chi_threshold:
                self.runbox.itemconfig(i, {'bg':'red'})
            else:
                self.runbox.itemconfig(i, {'bg':'white'})

        
            
            
            
            
