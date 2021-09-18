# fit_files tab for bfit
# Derek Fujimoto
# Dec 2017

from tkinter import *
from tkinter import ttk, messagebox, filedialog
from functools import partial
from bdata import bdata, bmerged
from bfit import logger_name, __version__
from scipy.special import gamma, polygamma
from pandas.plotting import register_matplotlib_converters
from multiprocessing import Queue

from bfit.gui.calculator_nqr_B0 import current2field
from bfit.gui.popup_show_param import popup_show_param
from bfit.gui.popup_param import popup_param
from bfit.gui.popup_fit_results import popup_fit_results
from bfit.gui.popup_fit_constraints import popup_fit_constraints
from bfit.gui.popup_add_param import popup_add_param
from bfit.gui.popup_ongoing_process import popup_ongoing_process
from bfit.fitting.decay_31mg import fa_31Mg
from bfit.fitting.functions import decay_corrected_fn
from bfit.backend.entry_color_set import on_focusout, on_entry_click
from bfit.backend.raise_window import raise_window
from bfit.gui.InputLine import InputLine

import numpy as np
import pandas as pd
import bdata as bd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import bfit.backend.colors as colors

import datetime, os, traceback, warnings, logging, yaml, textwrap

register_matplotlib_converters()

# =========================================================================== #
# =========================================================================== #
class fit_files(object):
    """
        Data fields:
            annotation:     stringvar: name of quantity for annotating parameters
            asym_type:      asymmetry calculation type
            canvas_frame_id:id number of frame in canvas
            chi_threshold:  if chi > thres, set color to red
            draw_components:list of titles for labels, options to export, draw.
            entry_asym_type:combobox for asym calculations
            fit_canvas:     canvas object allowing for scrolling
            par_label_entry:draw parameter label entry box
            pop_fitconstr:  object for fitting with constrained functions
            fit_data_tab:   containing frame (for destruction)
            fit_function_title: StringVar, title of fit function to use
            fit_function_title_box: combobox for fit function names
            fit_input:      fitting input values = (fn_name, ncomp, data_list)
            fit_lines:      Dict storing fitline objects
            fit_lines_old: dictionary of previously used fitline objects, keyed by run
            fit_routine_label: label for fit routine
            fitter:         fitting object from self.bfit.routine_mod
            gchi_label:     Label for global chisquared
            mode:           what type of run is this.

            n_component:    number of fitting components (IntVar)
            n_component_box:Spinbox for number of fitting components
            par_label       StringVar, label for plotting parameter set
            plt:            self.bfit.plt

            pop_addpar:     popup for ading parameters which are combinations of others
            pop_fitres:     modelling popup, for continuity between button presses
            pop_fitcontr:   popup for fitting constrained values

            probe_label:    Label for probe species
            runframe:       frame for displaying fit results and inputs
            runmode_label:  display run mode
            set_as_group:   BooleanVar() if true, set fit parfor whole group
            set_prior_p0:   BooleanVar() if true, set P0 of newly added runs to
                            P0 of fit with largest run number
            share_var:      BooleanVar() holds share checkbox for all fitlines
            use_rebin:      BoolVar() for rebinning on fitting
            xaxis:          StringVar() for parameter to draw on x axis
            yaxis:          StringVar() for parameter to draw on y axis
            xaxis_combobox: box for choosing x axis draw parameter
            yaxis_combobox: box for choosing y axis draw parameter

            xlo, hi:         StringVar, fit range limits on x axis
    """

    default_fit_functions = {
            '20':('Exp', 'Str Exp'),
            '2h':('Exp', 'Str Exp'),
            '1f':('Lorentzian', 'Gaussian'),
            '1x':('Lorentzian', 'Gaussian'),
            '1w':('Lorentzian', 'Gaussian'),
            '1n':('Lorentzian', 'Gaussian')}
    mode = ""
    chi_threshold = 1.5 # threshold for red highlight on bad fits
    n_fitx_pts = 500    # number of points to draw in fitted curves
    
    # ======================================================================= #
    def __init__(self, fit_data_tab, bfit):

        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing')

        # initialize
        self.bfit = bfit
        self.fit_output = {}
        self.share_var = {}
        self.fitter = self.bfit.routine_mod.fitter(keyfn = bfit.get_run_key,
                                                   probe_species = bfit.probe_species.get())
        self.draw_components = list(bfit.draw_components)
        self.fit_data_tab = fit_data_tab
        self.plt = self.bfit.plt

        # additional button bindings
        self.bfit.root.bind('<Control-Key-u>', self.update_param)

        # make top level frames
        mid_fit_frame = ttk.Labelframe(fit_data_tab,
                                       text='Set Initial Parameters', pad=5)

        mid_fit_frame.grid(column=0, row=1, rowspan=6, sticky=(S, W, E, N), padx=5, pady=5)

        fit_data_tab.grid_columnconfigure(0, weight=1)   # fitting space
        fit_data_tab.grid_rowconfigure(6, weight=1)      # push bottom window in right frame to top
        mid_fit_frame.grid_columnconfigure(0, weight=1)
        mid_fit_frame.grid_rowconfigure(0, weight=1)

        # TOP FRAME -----------------------------------------------------------

        # fit function select
        fn_select_frame = ttk.Labelframe(fit_data_tab, text='Fit Function')
        self.fit_function_title = StringVar()
        self.fit_function_title.set("")
        self.fit_function_title_box = ttk.Combobox(fn_select_frame,
                textvariable=self.fit_function_title, state='readonly')
        self.fit_function_title_box.bind('<<ComboboxSelected>>',
            lambda x :self.populate_param(force_modify=True))

        # number of components in fit spinbox
        self.n_component = IntVar()
        self.n_component.set(1)
        self.n_component_box = Spinbox(fn_select_frame, from_=1, to=20,
                textvariable=self.n_component, width=5,
                command=lambda:self.populate_param(force_modify=True))

        # fit and other buttons
        fit_button = ttk.Button(fn_select_frame, text='        Fit        ', command=self.do_fit, \
                                pad=1)
        constraint_button = ttk.Button(fn_select_frame, text='Constrained Fit',
                                       command=self.do_fit_constraints, pad=1)
        set_param_button = ttk.Button(fn_select_frame, text='   Set Result as P0   ',
                        command=self.do_set_result_as_initial, pad=1)
        reset_param_button = ttk.Button(fn_select_frame, text='     Reset P0     ',
                        command=self.do_reset_initial, pad=1)

        # GRIDDING

        # top frame gridding
        fn_select_frame.grid(column=0, row=0, sticky=(W, E, N), padx=5, pady=5)

        c = 0
        self.fit_function_title_box.grid(column=c, row=0, padx=5); c+=1
        ttk.Label(fn_select_frame, text="Number of Terms:").grid(column=c,
                  row=0, padx=5, pady=5, sticky=W); c+=1
        self.n_component_box.grid(column=c, row=0, padx=5, pady=5, sticky=W); c+=1
        fit_button.grid(column=c, row=0, padx=5, pady=1, sticky=W); c+=1
        constraint_button.grid(column=c, row=0, padx=5, pady=1, sticky=(W, E)); c+=1
        set_param_button.grid(column=c, row=0, padx=5, pady=1, sticky=W); c+=1
        reset_param_button.grid(column=c, row=0, padx=5, pady=1, sticky=W); c+=1

        # MID FRAME -----------------------------------------------------------

        # Scrolling frame to hold fitlines
        yscrollbar = ttk.Scrollbar(mid_fit_frame, orient=VERTICAL)
        self.fit_canvas = Canvas(mid_fit_frame, bd=0,                # make a canvas for scrolling
                yscrollcommand=yscrollbar.set,                      # scroll command receive
                scrollregion=(0, 0, 5000, 5000), confine=True)       # default size
        yscrollbar.config(command=self.fit_canvas.yview)            # scroll command send
        self.runframe = ttk.Frame(self.fit_canvas, pad=5)           # holds

        self.canvas_frame_id = self.fit_canvas.create_window((0, 0),    # make window which can scroll
                window=self.runframe,
                anchor='nw')
        self.runframe.bind("<Configure>", self.config_canvas) # bind resize to alter scrollable region
        self.fit_canvas.bind("<Configure>", self.config_runframe) # bind resize to change size of contained frame

        # gridding
        self.fit_canvas.grid(column=0, row=0, sticky=(E, W, S, N))
        yscrollbar.grid(column=1, row=0, sticky=(W, S, N))

        self.runframe.grid_columnconfigure(0, weight=1)
        self.fit_canvas.grid_columnconfigure(0, weight=1)
        self.fit_canvas.grid_rowconfigure(0, weight=1)

        self.runframe.bind("<Configure>", self.config_canvas) # bind resize to alter scrollable region
        self.fit_canvas.bind("<Configure>", self.config_runframe) # bind resize to change size of contained frame

        # RIGHT FRAME ---------------------------------------------------------

        # run mode
        fit_runmode_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Run Mode', )
        self.fit_runmode_label = ttk.Label(fit_runmode_label_frame, text="", justify=CENTER)

        # fitting routine
        fit_routine_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Minimizer', )
        self.fit_routine_label = ttk.Label(fit_routine_label_frame, text="",
                                           justify=CENTER)

        # probe species
        probe_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Probe', )
        self.probe_label = ttk.Label(probe_label_frame,
                                     text=self.bfit.probe_species.get(),
                                     justify=CENTER)

        # global chisquared
        gchi_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Global ChiSq', )
        self.gchi_label = ttk.Label(gchi_label_frame, text='', justify=CENTER)

        # asymmetry calculation
        asym_label_frame = ttk.Labelframe(fit_data_tab, pad=(5, 5, 5, 5),
                text='Asymmetry Calculation', )
        self.asym_type = StringVar()
        self.asym_type.set('')
        self.entry_asym_type = ttk.Combobox(asym_label_frame, \
                textvariable=self.asym_type, state='readonly', \
                width=20)
        self.entry_asym_type['values'] = ()

        # other settings
        other_settings_label_frame = ttk.Labelframe(fit_data_tab, pad=(10, 5, 10, 5),
                text='Switches', )

        # set as group checkbox
        self.set_as_group = BooleanVar()
        set_group_check = ttk.Checkbutton(other_settings_label_frame,
                text='Modify for all', \
                variable=self.set_as_group, onvalue=True, offvalue=False)
        self.set_as_group.set(False)

        # rebin checkbox
        self.use_rebin = BooleanVar()
        set_use_rebin = ttk.Checkbutton(other_settings_label_frame,
                text='Rebin data (set in fetch)', \
                variable=self.use_rebin, onvalue=True, offvalue=False)
        self.use_rebin.set(False)

        # set P0 as prior checkbox
        self.set_prior_p0 = BooleanVar()
        set_prior_p0 = ttk.Checkbutton(other_settings_label_frame,
                text='Set P0 of new run to prior result', \
                variable=self.set_prior_p0, onvalue=True, offvalue=False)
        self.set_prior_p0.set(False)

        # specify x axis --------------------
        xspecify_frame = ttk.Labelframe(fit_data_tab,
            text='Restrict x limits', pad=5)

        self.xlo = StringVar()
        self.xhi = StringVar()
        self.xlo.set('-inf')
        self.xhi.set('inf')

        entry_xspecify_lo = Entry(xspecify_frame, textvariable=self.xlo, width=10)
        entry_xspecify_hi = Entry(xspecify_frame, textvariable=self.xhi, width=10)
        label_xspecify = ttk.Label(xspecify_frame, text=" < x < ")

        # fit results -----------------------
        results_frame = ttk.Labelframe(fit_data_tab,
            text='Fit Results and Run Conditions', pad=5)     # draw fit results

        # draw and export buttons
        button_frame = Frame(results_frame)
        draw_button = ttk.Button(button_frame, text='Draw', command=self.draw_param)
        update_button = ttk.Button(button_frame, text='Update', command=self.update_param)
        export_button = ttk.Button(button_frame, text='Export', command=self.export)
        show_button = ttk.Button(button_frame, text='Compare', command=self.show_all_results)
        model_fit_button = ttk.Button(button_frame, text='Fit a\nModel',
                                      command=self.do_fit_model)

        # menus for x and y values
        x_button = ttk.Button(results_frame, text="x axis:", command=self.do_add_param, pad=0)
        y_button = ttk.Button(results_frame, text="y axis:", command=self.do_add_param, pad=0)
        ann_button = ttk.Button(results_frame, text=" Annotation:", command=self.do_add_param, pad=0)
        label_label = ttk.Label(results_frame, text="Label:")

        self.xaxis = StringVar()
        self.yaxis = StringVar()
        self.annotation = StringVar()
        self.par_label = StringVar()

        self.xaxis.set('')
        self.yaxis.set('')
        self.annotation.set('')
        self.par_label.set('')

        self.xaxis_combobox = ttk.Combobox(results_frame, textvariable=self.xaxis,
                                      state='readonly', width=19)
        self.yaxis_combobox = ttk.Combobox(results_frame, textvariable=self.yaxis,
                                      state='readonly', width=19)
        self.annotation_combobox = ttk.Combobox(results_frame,
                                      textvariable=self.annotation,
                                      state='readonly', width=19)
        self.par_label_entry = Entry(results_frame,
                                    textvariable=self.par_label, width=21)

        # gridding
        button_frame.grid(column=0, row=0, columnspan=2)
        draw_button.grid(column=0, row=0, padx=5, pady=5)
        update_button.grid(column=0, row=1, padx=5, pady=5)
        show_button.grid(column=1, row=0, padx=5, pady=5)
        export_button.grid(column=1, row=1, padx=5, pady=5)
        model_fit_button.grid(column=2, row=0, rowspan=2, pady=5, sticky=(N, S))

        x_button.grid(column=0, row=1, sticky=(E, W), padx=5)
        y_button.grid(column=0, row=2, sticky=(E, W), padx=5)
        ann_button.grid(column=0, row=3, sticky=(E, W), padx=5)
        label_label.grid(column=0, row=4, sticky=(E, W), padx=10)

        self.xaxis_combobox.grid(column=1, row=1, pady=5)
        self.yaxis_combobox.grid(column=1, row=2, pady=5)
        self.annotation_combobox.grid(column=1, row=3, pady=5)
        self.par_label_entry.grid(column=1, row=4, pady=5)

        # save/load state -----------------------
        state_frame = ttk.Labelframe(fit_data_tab, text='Program State', pad=5)
        state_save_button = ttk.Button(state_frame, text='Save', command=self.bfit.save_state)
        state_load_button = ttk.Button(state_frame, text='Load', command=self.bfit.load_state)

        state_save_button.grid(column=1, row=0, padx=5, pady=5)
        state_load_button.grid(column=2, row=0, padx=5, pady=5)
        state_frame.columnconfigure([0, 3], weight=1)

        # gridding
        fit_runmode_label_frame.grid(column=1, row=0, pady=5, padx=2, sticky=(N, E, W))
        self.fit_runmode_label.grid(column=0, row=0, sticky=(E, W))

        fit_routine_label_frame.grid(column=2, row=0, pady=5, padx=2, sticky=(N, E, W))
        self.fit_routine_label.grid(column=0, row=0, sticky=(E, W))

        probe_label_frame.grid(column=1, row=1, columnspan=1, sticky=(E, W, N), pady=2, padx=2)
        self.probe_label.grid(column=0, row=0)

        gchi_label_frame.grid(column=2, row=1, columnspan=1, sticky=(E, W, N), pady=2, padx=2)
        self.gchi_label.grid(column=0, row=0)

        asym_label_frame.grid(column=1, row=2, columnspan=2, sticky=(E, W, N), pady=2, padx=2)
        asym_label_frame.columnconfigure([0, 2], weight=1)
        self.entry_asym_type.grid(column=1, row=0)

        other_settings_label_frame.grid(column=1, row=3, columnspan=2, sticky=(E, W, N), pady=2, padx=2)
        set_group_check.grid(column=0, row=0, padx=5, pady=1, sticky=W)
        set_use_rebin.grid(column=0, row=1, padx=5, pady=1, sticky=W)
        set_prior_p0.grid(column=0, row=2, padx=5, pady=1, sticky=W)

        entry_xspecify_lo.grid(column=1, row=0)
        label_xspecify.grid(column=2, row=0)
        entry_xspecify_hi.grid(column=3, row=0)
        xspecify_frame.columnconfigure([0, 4], weight=1)

        xspecify_frame.grid(column=1, row=4, columnspan=2, sticky=(E, W, N), pady=2, padx=2)
        results_frame.grid(column=1, row=5, columnspan=2, sticky=(E, W, N), pady=2, padx=2)
        state_frame.grid(column=1, row=6, columnspan=2, sticky=(E, W, N), pady=2, padx=2)

        # resizing

        # fn select
        fn_select_frame.grid_columnconfigure(1, weight=1)    # Nterms label
        fn_select_frame.grid_columnconfigure(4, weight=100)    # constraints
        fn_select_frame.grid_columnconfigure(5, weight=1)  # set results as p0
        fn_select_frame.grid_columnconfigure(6, weight=1)  # reset p0

        # fitting frame
        self.fit_canvas.grid_columnconfigure(0, weight=1)    # fetch frame
        self.fit_canvas.grid_rowconfigure(0, weight=1)

        # right frame
        for i in range(2):
            results_frame.grid_columnconfigure(i, weight=0)

        # store lines for fitting
        self.fit_lines = {}
        self.fit_lines_old = {}

    # ======================================================================= #
    def __del__(self):

        if hasattr(self, 'fit_lines'):       del self.fit_lines
        if hasattr(self, 'fit_lines_old'):   del self.fit_lines_old
        if hasattr(self, 'fitter'):          del self.fitter

        # kill buttons and frame
        try:
            for child in self.fetch_data_tab.winfo_children():
                child.destroy()
            self.fetch_data_tab.destroy()
        except Exception:
            pass

     # ======================================================================= #
    def _annotate(self, id, x, y, ptlabels, color='k', unique=True):
        """Add annotation"""

        # base case
        if ptlabels is None: return

        # do annotation
        for label, xcoord, ycoord in zip(ptlabels, x, y):
            if type(label) != type(None):
                self.plt.annotate('param', id, label,
                             xy=(xcoord, ycoord),
                             xytext=(-3, 20),
                             textcoords='offset points',
                             ha='right',
                             va='bottom',
                             bbox=dict(boxstyle='round, pad=0.1',
                                       fc=color,
                                       alpha=0.1),
                             arrowprops=dict(arrowstyle = '->',
                                             connectionstyle='arc3, rad=0'),
                             fontsize='xx-small',
                             unique=unique
                            )

    # ======================================================================= #
    def _make_shared_var_dict(self):
        """Make the dictionary to make sure all shared checkboxes are synched"""

        # get parameter list
        try:
            parlst = [p for p in self.fitter.gen_param_names(
                                                self.fit_function_title.get(),
                                                self.n_component.get())]

        # no paramteters: empty out the variable list
        except KeyError:
            share_var = {}

        # make new shared list
        else:
            # re-initialize
            share_var = {p:BooleanVar() for p in parlst}

            # set to old values if they exist
            for p in parlst:
                if p in self.share_var.keys():
                    share_var[p].set(self.share_var[p].get())

        # save to object
        self.share_var = share_var

    # ======================================================================= #
    def canvas_scroll(self, event):
        """Scroll canvas with files selected."""
        if event.num == 4:
            self.fit_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.fit_canvas.yview_scroll(1, "units")

    # ======================================================================= #
    def config_canvas(self, event):
        """Alter scrollable region based on canvas bounding box size.
        (changes scrollbar properties)"""
        self.fit_canvas.configure(scrollregion=self.fit_canvas.bbox("all"))

    # ======================================================================= #
    def config_runframe(self, event):
        """Alter size of contained frame in canvas. Allows for inside window to
        be resized with mouse drag"""
        self.fit_canvas.itemconfig(self.canvas_frame_id, width=event.width)

    # ======================================================================= #
    def populate(self, *args):
        """
            Make tabs for setting fit input parameters.
        """

        # get data
        dl = self.bfit.fetch_files.data_lines
        keylist = [k for k in dl.keys() if dl[k].check_state.get()]
        keylist.sort()
        self.logger.debug('Populating data for %s', keylist)

        # get run mode by looking at one of the data dictionary keys
        for key_zero in self.bfit.data.keys(): break

        # create fit function combobox options
        try:
            if self.mode != self.bfit.data[key_zero].mode:

                # set run mode
                self.mode = self.bfit.data[key_zero].mode
                self.fit_runmode_label['text'] = \
                        self.bfit.fetch_files.runmode_relabel[self.mode]
                self.logger.debug('Set new run mode %s', self.mode)

                # set routine
                self.fit_routine_label['text'] = self.fitter.__name__

                # set run functions
                fn_titles = self.fitter.function_names[self.mode]
                self.fit_function_title_box['values'] = fn_titles
                if self.fit_function_title.get() == '':
                    self.fit_function_title.set(fn_titles[0])

        except UnboundLocalError:
            self.fit_function_title_box['values'] = ()
            self.fit_function_title.set("")
            self.fit_runmode_label['text'] = ""
            self.mode = ""

        # make shared_var dictionary
        self._make_shared_var_dict()

        # delete unused fitline objects
        for k in list(self.fit_lines.keys()):       # iterate fit list
            self.fit_lines[k].degrid()
            if k not in keylist:                    # check data list
                self.fit_lines_old[k] = self.fit_lines[k]
                del self.fit_lines[k]

        # make or regrid fitline objects
        n = 0
        for k in keylist:
            if k not in self.fit_lines.keys():
                if k in self.fit_lines_old.keys():
                    self.fit_lines[k] = self.fit_lines_old[k]
                else:
                    self.fit_lines[k] = fitline(self.bfit, self.runframe, dl[k], n)
            self.fit_lines[k].grid(n)
            n+=1

        self.populate_param()

    # ======================================================================= #
    def populate_param(self, *args, force_modify=False):
        """
            Populate the list of parameters

            force_modify: passed to line.populate
        """

        self.logger.debug('Populating fit parameters')

        # populate axis comboboxes
        lst = self.draw_components.copy()

        try:
            parlst = [p for p in self.fitter.gen_param_names(
                                                self.fit_function_title.get(),
                                                self.n_component.get())]
        except KeyError:
            self.xaxis_combobox['values'] = []
            self.yaxis_combobox['values'] = []
            self.annotation_combobox['values'] = []
            return

        # Sort the parameters
        parlst.sort()

        # add parameter beta averaged T1
        if self.fit_function_title.get() == 'Str Exp':
            ncomp = self.n_component.get()

            if ncomp > 1:
                for i in range(ncomp):
                    parlst.append('Beta-Avg 1/<T1>_%d' % i)
            else:
                parlst.append('Beta-Avg 1/<T1>')

        # add parameter T1 not 1/T1
        if 'Exp' in self.fit_function_title.get():
            ncomp = self.n_component.get()

            if ncomp > 1:
                for i in range(ncomp):
                    parlst.append('T1_%d' % i)
                    
                    if self.fit_function_title.get() == 'Bi Exp':
                        parlst.append('T1b_%d' % i)
                    
            else:
                parlst.append('T1')
                
                if self.fit_function_title.get() == 'Bi Exp':
                    parlst.append('T1b')

        self.xaxis_combobox['values'] = [''] + parlst + lst
        self.yaxis_combobox['values'] = [''] + parlst + lst
        self.annotation_combobox['values'] = [''] + parlst + lst

        self._make_shared_var_dict()

        # turn off modify all so we don't cause an infinite loop
        modify_all_value = self.set_as_group.get()
        self.set_as_group.set(False)

        # regenerate fitlines
        for k in self.fit_lines.keys():
            self.fit_lines[k].populate(force_modify=force_modify)

        # reset modify all value
        self.set_as_group.set(modify_all_value)
        
    # ======================================================================= #
    def do_add_param(self, *args):
        """Launch popup for adding user-defined parameters to draw"""

        self.logger.info('Launching add paraemeter popup')

        if hasattr(self, 'pop_addpar'):
            p = self.pop_addpar

            # don't make more than one window
            if Toplevel.winfo_exists(p.win):
                p.win.lift()
                return

            # make a new window, using old inputs and outputs
            self.pop_addpar = popup_add_param(self.bfit,
                                    input_fn_text=p.input_fn_text)

        # make entirely new window
        else:
            self.pop_addpar = popup_add_param(self.bfit)

    # ======================================================================= #
    def do_end_of_fit(self):
        """Things to do after fitting: draw, set checkbox status"""

        # enable fit checkboxes on fetch files tab
        for k in self.bfit.fetch_files.data_lines.keys():
            dline = self.bfit.fetch_files.data_lines[k]
            dline.draw_fit_checkbox['state'] = 'normal'
            dline.draw_res_checkbox['state'] = 'normal'
            dline.check_fit.set(True)
        self.bfit.fetch_files.check_state_fit.set(True)

        # change fetch asymmetry mode to match fit tab
        inv_map = {v: k for k, v in self.bfit.asym_dict.items()}
        asym_mode_fit = inv_map[self.bfit.get_asym_mode(self)]
        asym_mode_fetch = inv_map[self.bfit.get_asym_mode(self.bfit.fetch_files)]
        
        self.bfit.fetch_files.asym_type.set(asym_mode_fit)

        # draw fit results
        if self.bfit.draw_fit.get():
            style = self.bfit.draw_style.get()

            if style in ['stack', 'new']:
                self.bfit.draw_style.set('redraw')

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self.bfit.fetch_files.draw_all(figstyle='fit', ignore_check=False)

            if len(self.fit_lines.keys()) > self.bfit.legend_max_draw:

                try:
                    self.plt.gca('fit').get_legend().remove()
                except AttributeError:
                    pass
                else:
                    self.plt.tight_layout('fit')

            # reset style
            self.bfit.draw_style.set(style)
            
        # reset asym mode
        self.bfit.fetch_files.asym_type.set(asym_mode_fetch)
    
    # ======================================================================= #
    def do_fit(self, *args):
        # fitter
        fitter = self.fitter
        figstyle = 'fit'

        # get fitter inputs
        fn_name = self.fit_function_title.get()
        ncomp = self.n_component.get()

        xlims = [self.xlo.get(), self.xhi.get()]
        if not xlims[0]:
            xlims[0] = '-inf'
            self.xlo.set('-inf')
        if not xlims[1]:
            xlims[1] = 'inf'
            self.xhi.set('inf')

        try:
            xlims = tuple(map(float, xlims))
        except ValueError as err:
            messagebox.showerror("Error", 'Bad input for xlims')
            self.logger.exception(str(err))
            raise err

        self.logger.info('Fitting with "%s" with %d components', fn_name, ncomp)

        # build data list
        data_list = []
        for key in self.fit_lines:

            # get fit line
            fitline = self.fit_lines[key]

            # bdata object
            bdfit = fitline.dataline.bdfit

            # pdict
            pdict = {}
            for parname in fitline.parentry.keys():

                # get entry values
                pline = fitline.parentry[parname]
                line = []
                for col in fitline.collist:

                    # get number entries
                    if col in ('p0', 'blo', 'bhi'):
                        try:
                            line.append(float(pline[col][0].get()))
                        except ValueError as errmsg:
                            self.logger.exception("Bad input.")
                            messagebox.showerror("Error", str(errmsg))
                            raise errmsg

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

            if self.use_rebin.get():
                doptions['rebin'] = bdfit.rebin.get()

            if self.mode in ('1f', '1w', '1x'):
                dline = self.bfit.fetch_files.data_lines[key]
                doptions['omit'] = dline.bin_remove.get()
                if doptions['omit'] == dline.bin_remove_starter_line:
                    doptions['omit'] = ''
            elif self.mode in ('20', '2h', '2e'):
                pass
            else:
                msg = 'Fitting mode %s not recognized' % self.mode
                self.logger.error(msg)
                raise RuntimeError(msg)

            # make data list
            data_list.append([bdfit, pdict, doptions])

        # call fitter with error message, potentially
        self.fit_input = (fn_name, ncomp, data_list)

        # set up queue
        que = Queue()

        def run_fit():
            try:
                # fit_output keyed as {run:[key/par/cov/chi/fnpointer]}
                fit_output = fitter(fn_name=fn_name,
                                    ncomp=ncomp,
                                    data_list=data_list,
                                    hist_select=self.bfit.hist_select,
                                    asym_mode=self.bfit.get_asym_mode(self),
                                    xlims=xlims)
            except Exception as errmsg:
                self.logger.exception('Fitting error')
                que.put(str(errmsg))
                raise errmsg from None

            que.put(fit_output)

        # log fitting
        for d in data_list:
            self.logger.info('Fitting run %s: %s', self.bfit.get_run_key(d[0]), d[1:])

        # start fit
        popup = popup_ongoing_process(self.bfit,
                    target = run_fit,
                    message="Fitting in progress...",
                    queue = que,
                    do_disable = lambda : self.input_enable_disable(self.fit_data_tab, state='disabled'),
                    do_enable = lambda : self.input_enable_disable(self.fit_data_tab, state='normal'),
                    )
        output = popup.run()

        # fit success
        if type(output) is tuple: 
            fit_output, gchi = output

        # error message
        elif type(output) is str:
            messagebox.showerror("Error", output)
            return

        # fit cancelled
        elif output is None:
            return

        # get fit functions
        fns = fitter.get_fit_fn(fn_name, ncomp, data_list)
        
        # set output results
        for key, df in fit_output.items(): # iterate run ids
            
            # get fixed and shared
            parentry = self.fit_lines[key].parentry
            keylist = tuple(parentry.keys())
            fs = {'fixed':[], 'shared':[], 'parnames':keylist}
            
            for kk in keylist:  # iterate parameters
                fs['fixed'].append(parentry[kk]['fixed'][0].get())
                fs['shared'].append(parentry[kk]['shared'][0].get())
            
            df2 = pd.concat((df, pd.DataFrame(fs).set_index('parnames')), axis='columns')
            
            # make output
            new_output = {'results': df2, 
                          'fn': fns[key],
                          'gchi': gchi}
                          
            self.bfit.data[key].set_fitresult(new_output)
            self.bfit.data[key].fit_title = self.fit_function_title.get()
            self.bfit.data[key].ncomp = self.n_component.get()

        # display run results
        for key in self.fit_lines.keys():
            self.fit_lines[key].show_fit_result()

        # show global chi
        self.gchi_label['text'] = str(np.around(gchi, 2))

        self.do_end_of_fit()

    # ======================================================================= #
    def do_fit_constraints(self):

        self.logger.info('Launching fit constraints popup')

        if hasattr(self, 'pop_fitconstr'):
            p = self.pop_fitconstr

            # don't make more than one window
            if Toplevel.winfo_exists(p.win):
                p.win.lift()
                return

            # make a new window, using old inputs and outputs
            self.pop_fitconstr = popup_fit_constraints(self.bfit,
                                    output_par_text=p.output_par_text_val,
                                    output_text=p.output_text_val)

        # make entirely new window
        else:
            self.pop_fitconstr = popup_fit_constraints(self.bfit)

    # ======================================================================= #
    def do_fit_model(self):

        self.logger.info('Launching fit model popup')

        if hasattr(self, 'pop_fitres'):
            p = self.pop_fitres

            # don't make more than one window
            if Toplevel.winfo_exists(p.win):
                p.win.lift()
                return

            # make a new window, using old inputs and outputs
            self.pop_fitres = popup_fit_results(self.bfit,
                                    input_fn_text=p.input_fn_text,
                                    output_par_text=p.output_par_text_val,
                                    output_text=p.output_text_val,
                                    chi=p.chi,
                                    x = p.xaxis.get(),
                                    y = p.yaxis.get())

        # make entirely new window
        else:
            self.pop_fitres = popup_fit_results(self.bfit)

    # ======================================================================= #
    def do_gui_param(self, id=''):
        """Set initial parmeters with GUI"""

        self.logger.info('Launching initial fit parameters popup')
        popup_param(self.bfit, id)

    # ======================================================================= #
    def do_set_result_as_initial(self, *args):
        """Set initial parmeters as the fitting results"""

        self.logger.info('Setting initial parameters as fit results')

        # turn off modify all
        modify_all_value = self.set_as_group.get()
        self.set_as_group.set(False)

        # set result to initial value
        for k in self.fit_lines.keys():

            # get line
            line = self.fit_lines[k]

            # get parameters
            parentry = line.parentry

            # set
            for p in parentry.keys():
                parentry[p]['p0'][0].set(parentry[p]['res'][0].get())

        # reset modify all setting
        self.set_as_group.set(modify_all_value)

    # ======================================================================= #
    def do_reset_initial(self, *args):
        """Reset initial parmeters to defaults"""

        self.logger.info('Reset initial parameters')

        for k in self.fit_lines.keys():
            self.fit_lines[k].populate(force_modify=True)

    # ======================================================================= #
    def draw_param(self, *args):
        """Draw the fit parameters"""
        figstyle = 'param'

        # make sure plot shows
        plt.ion()

        # get draw components
        xdraw = self.xaxis.get()
        ydraw = self.yaxis.get()
        ann = self.annotation.get()
        label = self.par_label.get()

        self.logger.info('Draw fit parameters "%s" vs "%s" with annotation "%s"'+\
                         ' and label %s', ydraw, xdraw, ann, label)

        # get plottable data
        try:
            xvals, xerrs = self.get_values(xdraw)
            yvals, yerrs = self.get_values(ydraw)
        except UnboundLocalError as err:
            self.logger.error('Bad input parameter selection')
            messagebox.showerror("Error", 'Select two input parameters')
            raise err from None
        except (KeyError, AttributeError) as err:
            self.logger.error('Parameter "%s or "%s" not found for drawing',
                              xdraw, ydraw)
            messagebox.showerror("Error",
                    'Drawing parameter "%s" or "%s" not found' % (xdraw, ydraw))
            raise err from None

        # get asymmetric errors
        if type(xerrs) is tuple:
            xerrs_l = xerrs[0]
            xerrs_h = xerrs[1]
        else:
            xerrs_l = xerrs
            xerrs_h = xerrs

        if type(yerrs) is tuple:
            yerrs_l = yerrs[0]
            yerrs_h = yerrs[1]
        else:
            yerrs_l = yerrs
            yerrs_h = yerrs

        # get annotation
        if ann != '':
            try:
                ann, _ = self.get_values(ann)
            except UnboundLocalError:
                ann = None
            except (KeyError, AttributeError) as err:
                self.logger.error('Bad input annotation value "%s"', ann)
                messagebox.showerror("Error",
                        'Annotation "%s" not found' % (ann))
                raise err from None

        # fix annotation values (blank to none)
        else:
            ann = None

        # get mouseover annotation labels
        mouse_label, _ = self.get_values('Unique Id')

        # sort by x values
        idx = np.argsort(xvals)
        xvals = np.asarray(xvals)[idx]
        yvals = np.asarray(yvals)[idx]

        xerrs_l = np.asarray(xerrs_l)[idx]
        yerrs_l = np.asarray(yerrs_l)[idx]
        xerrs_h = np.asarray(xerrs_h)[idx]
        yerrs_h = np.asarray(yerrs_h)[idx]

        if ann is not None:
            ann = np.asarray(ann)[idx]

        mouse_label = np.asarray(mouse_label)[idx]

        # fix annotation values (round floats)
        if ann is not None:
            number_string = '%.'+'%df' % self.bfit.rounding
            for i, a in enumerate(ann):
                if type(a) in [float, np.float64]:
                    ann[i] = number_string % np.around(a, self.bfit.rounding)

        # get default data_id
        if label:
            draw_id = label
        else:
            draw_id = ''

            if self.bfit.draw_style.get() == 'stack':
                ax = self.plt.gca(figstyle)

        # make new window
        style = self.bfit.draw_style.get()
        if style == 'new' or not self.plt.active[figstyle]:
            self.plt.figure(figstyle)
        elif style == 'redraw':
            self.plt.clf(figstyle)

        # get axis
        ax = self.plt.gca(figstyle)

        # set dates axis
        if xdraw in ('Start Time', ):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m/%d (%H:%M)'))
            xvals = np.array([datetime.datetime.fromtimestamp(x) for x in xvals])
            xerrs = None
            ax.tick_params(axis='x', which='major', labelsize='x-small')
        else:
            try:
                ax.get_xaxis().get_major_formatter().set_useOffset(False)
            except AttributeError:
                pass

        if ydraw in ('Start Time', ):
            ax.yaxis.set_major_formatter(mdates.DateFormatter('%y/%m/%d (%H:%M)'))
            yvals = mdates.epoch2num(yvals)
            yerrs = None
            ax.tick_params(axis='y', which='major', labelsize='x-small')
        else:
            try:
                ax.get_yaxis().get_major_formatter().set_useOffset(False)
            except AttributeError:
                pass

        # remove component label
        ncomp = self.n_component.get()
        xsuffix = ''
        ysuffix = ''
        
        if ncomp > 1:

            fn_params = self.fitter.gen_param_names(self.fit_function_title.get(), ncomp)
                        
            if xdraw in fn_params or 'Beta-Avg 1/<T1>' in xdraw or 'T1' in xdraw:
                spl = xdraw.split('_')
                xdraw = '_'.join(spl[:-1])
                xsuffix = ' [%s]' % spl[-1]

            if ydraw in fn_params or 'Beta-Avg 1/<T1>' in ydraw or 'T1' in ydraw:
                spl = ydraw.split('_')
                ydraw = '_'.join(spl[:-1])
                ysuffix = ' [%s]' % spl[-1]
             
        # pretty labels
        xdraw = self.fitter.pretty_param.get(xdraw, xdraw)
        ydraw = self.fitter.pretty_param.get(ydraw, ydraw)

        # add suffix for multiple labels
        xdraw = xdraw + xsuffix
        ydraw = ydraw + ysuffix

        # attempt to insert units and scale
        unit_scale, unit = self.bfit.units.get(self.mode, [1, ''])
        if '%s' in xdraw:
            xdraw = xdraw % unit
            xvals *= unit_scale
            xerrs_h *= unit_scale
            xerrs_l *= unit_scale
        if '%s' in ydraw:
            ydraw = ydraw % unit
            yvals *= unit_scale
            yerrs_h *= unit_scale
            yerrs_l *= unit_scale

        # check for nan errors
        if all(np.isnan(xerrs_h)): xerrs_h = None
        if all(np.isnan(xerrs_l)): xerrs_l = None
        if all(np.isnan(yerrs_h)): yerrs_h = None
        if all(np.isnan(yerrs_l)): yerrs_l = None

        if xerrs_h is None and xerrs_l is None:     xerr = None
        else:                                       xerr = (xerrs_l, xerrs_h)
        if yerrs_h is None and yerrs_l is None:     yerr = None
        else:                                       yerr = (yerrs_l, yerrs_h)

        # draw
        f = self.plt.errorbar(  figstyle,
                                draw_id,
                                xvals,
                                yvals,
                                xerr = xerr,
                                yerr = yerr,
                                label=draw_id,
                                annot_label=mouse_label,
                                **self.bfit.style)
        self._annotate(draw_id, xvals, yvals, ann, color=f[0].get_color(), unique=False)

        # format date x axis
        if xerrs is None:   self.plt.gcf(figstyle).autofmt_xdate()
        
        # plot elements
        self.plt.xlabel(figstyle, xdraw)
        self.plt.ylabel(figstyle, ydraw)
        self.plt.tight_layout(figstyle)

        if draw_id:
            self.plt.legend(figstyle, fontsize='x-small')

        # bring window to front
        raise_window()

    # ======================================================================= #
    def export(self, savetofile=True, filename=None):
        """Export the fit parameter and file headers"""
        # get values and errors
        val = {}

        for v in self.xaxis_combobox['values']:
            if v == '': continue

            try:
                v2 = self.get_values(v)

            # value not found
            except (KeyError, AttributeError):
                continue

            # if other error, don't crash but print the result
            except Exception:
                traceback.print_exc()
            else:
                val[v] = v2[0]

                if type(v2[1]) is tuple:
                    val['Error- '+v] = v2[1][0]
                    val['Error+ '+v] = v2[1][1]
                else:
                    val['Error '+v] = v2[1]

        # get fixed and shared
        keylist = []
        for k, line in self.fit_lines.items():
            keylist.append(k)
            data = line.dataline.bdfit
            
            for kk in data.fitpar.index:
                
                name = 'fixed '+kk
                if name not in val.keys(): val[name] = []
                val[name].append(data.fitpar.loc[kk, 'fixed'])
                
                name = 'shared '+kk
                if name not in val.keys(): val[name] = []
                val[name].append(data.fitpar.loc[kk, 'shared'])

        # get shared and fixed parameters
        # make data frame for output
        df = pd.DataFrame(val)
        df.set_index('Run Number', inplace=True)

        # drop completely empty columns
        bad_cols = [c for c in df.columns if all(df[c].isna())]
        for c in bad_cols:
            df.drop(c, axis='columns', inplace=True)

        if savetofile:

            # get file name
            if filename is None:
                filename = filedialog.asksaveasfilename(filetypes=[('csv', '*.csv'),
                                                                   ('allfiles', '*')],
                                                    defaultextension='.csv')
                if not filename:    
                    return
            self.logger.info('Exporting parameters to "%s"', filename)

            # check extension
            if os.path.splitext(filename)[1] == '':
                filename += '.csv'

            # write header
            data = self.bfit.data[list(self.fit_lines.keys())[0]]

            if hasattr(data, 'fit_title'):
                header = ['# Fit function : %s' % data.fit_title,
                          '# Number of components: %d' % data.ncomp,
                          '# Global Chi-Squared: %s' % self.gchi_label['text']
                          ]
            else:
                header = []

            header.extend(['# Generated by bfit v%s on %s' % (__version__, datetime.datetime.now()),
                          '#\n#\n'])

            with open(filename, 'w') as fid:
                fid.write('\n'.join(header))

            # write data
            df.to_csv(filename, mode='a+')
            self.logger.debug('Export success')
        else:
            self.logger.info('Returned exported parameters')
            return df

    # ======================================================================= #
    def export_fit(self, savetofile=True, directory=None):
        """Export the fit lines as csv files"""

        # filename
        filename = self.bfit.fileviewer.default_export_filename
        filename = '_fit'.join(os.path.splitext(filename))

        if directory is None:
            directory = filedialog.askdirectory()
            if not directory:
                return
        
        filename = os.path.join(directory, filename)

        # asymmetry type
        asym_mode = self.bfit.get_asym_mode(self)

        # get data and write
        for id in self.fit_lines.keys():

            # get data
            data = self.bfit.data[id]
            t, a, da = data.asym(asym_mode)

            # get fit data
            fitx = np.linspace(min(t), max(t), self.n_fitx_pts)

            try:
                fit_par = data.fitpar.loc[data.parnames, 'res']
            except AttributeError:
                continue
            dfit_par_l = data.fitpar.loc[data.parnames, 'dres-']
            dfit_par_h = data.fitpar.loc[data.parnames, 'dres+']
            fity = data.fitfn(fitx, *fit_par)

            if data.mode in self.bfit.units:
                unit = self.bfit.units[data.mode]
                fitxx = fitx*unit[0]
                xlabel = self.bfit.xlabel_dict[self.mode] % unit[1]
            else:
                fitxx = fitx
                xlabel = self.bfit.xlabel_dict[self.mode]

            # write header
            fname = filename%(data.year, data.run)
            header = ['# %s' % data.id,
                      '# %s' % data.title,
                      '# Fit function : %s' % data.fit_title,
                      '# Number of components: %d' % data.ncomp,
                      '# Rebin: %d' % data.rebin.get(),
                      '# Bin Omission: %s' % data.omit.get().replace(
                                self.bfit.fetch_files.bin_remove_starter_line, ''),
                      '# Chi-Squared: %f' % data.chi,
                      '# Parameter names: %s' % ', '.join(data.parnames),
                      '# Parameter values: %s' % ', '.join(list(map(str, fit_par))),
                      '# Parameter errors (-): %s' % ', '.join(list(map(str, dfit_par_l))),
                      '# Parameter errors (+): %s' % ', '.join(list(map(str, dfit_par_h))),
                      '#',
                      '# Generated by bfit v%s on %s' % (__version__, datetime.datetime.now()),
                      '#']

            with open(fname, 'w') as fid:
                fid.write('\n'.join(header) + '\n')

            # write data
            df = pd.DataFrame({xlabel:fitx, 'asymmetry':fity})
            df.to_csv(fname, index=False, mode='a+')
            self.logger.info('Exporting fit to %s', fname)

    # ======================================================================= #
    def get_values(self, select):
        """ Get plottable values from all runs"""
        
        data = self.bfit.data
        dlines = self.bfit.fetch_files.data_lines

        # draw only selected runs
        runs = [dlines[k].id for k in dlines if dlines[k].check_state.get()]
        runs.sort()

        self.logger.debug('Fetching parameter %s', select)
        
        # get values
        out = np.array([data[r].get_values(select) for r in runs], dtype=object)
        
        val = out[:, 0]
        err = np.array(out[:, 1].tolist())
        if len(err.shape) > 1: 
            err = (err[:, 0], err[:, 1])
        
        return (val, err)
        
    # ======================================================================= #
    def input_enable_disable(self, parent, state, first=True):
        """
            Prevent input while fitting by disabling options

            state: "disabled" or "normal"
            first: do non-recursive items (i.e. menus, tabs)
        """

        if first:

            # disable tabs
            self.bfit.notebook.tab(1, state=state)

            # disable menu options
            file = self.bfit.menus['File']
            file.entryconfig("Run Commands", state=state)
            file.entryconfig("Export Fits", state=state)
            file.entryconfig("Save State", state=state)
            file.entryconfig("Load State", state=state)

            settings = self.bfit.menus['Settings']
            settings.entryconfig("Probe Species", state=state)

            draw_mode = self.bfit.menus['Draw Mode']
            draw_mode.entryconfig("Use NBM in asymmetry", state=state)
            draw_mode.entryconfig("Draw 1f/1x as PPM shift", state=state)

            self.bfit.menus['menubar'].entryconfig("Minimizer", state=state)

        # disable everything in fit_tab
        for child in parent.winfo_children():
            try:
                if state == 'disabled':
                    child.old_state = child['state']
                    child.configure(state=state)
                else:
                    child.configure(state=child.old_state)
            except (TclError, AttributeError):
                pass
            self.input_enable_disable(child, state=state, first=False)

    # ======================================================================= #
    def set_lines(self, pname, col, value):
        """
            Modify all input fields of each line to match the altered one
            conditional on self.set_as_group

            pname: string, parameter being changed
            col:   str, column being changed
            value: new value to assign
        """
    
        for fitline in self.fit_lines.values():
            
            # get line id
            id = [line.pname for line in fitline.lines].index(pname)
            line = fitline.lines[id]
            
            # set 
            line.set(**{col:value})        

    # ======================================================================= #
    def return_binder(self):
        """
            Binding to entery key press, depending on focus.

            FOCUS                   ACTION

            comboboxes or buttons   draw_param
                in right frame
            else                    do_fit
        """

        # get focus
        focus = self.bfit.root.focus_get()

        # right frame items
        draw_par_items = (  self.xaxis_combobox,
                            self.yaxis_combobox,
                            self.annotation_combobox,
                            self.par_label_entry)

        # do action
        if focus in draw_par_items:
            self.draw_param()
        elif focus == self.n_component_box:
            self.populate_param(force_modify=True)
        elif focus == self.bfit.root:
            pass
        else:
            self.do_fit()

    # ======================================================================= #
    def show_all_results(self):
        """Make a window to display table of fit results"""

        self.logger.info('Launching parameter table popup')

        # get fit results
        df = self.export(savetofile=False)
        popup_show_param(df)

    # ======================================================================= #
    def update_param(self, *args):
        """Update all figures with parameters drawn with new fit results"""

        self.logger.info('Updating parameter figures')

        # get list of figure numbers for parameters
        figlist = self.plt.plots['param']

        # set style to redraw
        current_active = self.plt.active['param']
        current_style = self.bfit.draw_style.get()
        self.bfit.draw_style.set('stack')

        # get current labels
        current_xlab = self.xaxis.get()
        current_ylab = self.yaxis.get()

        # get current unit
        unit = self.bfit.units[self.mode]

        # back-translate pretty labels to originals
        ivd = {}
        for  k, v in self.fitter.pretty_param.items():
            
            try:
                v = v % unit[1]
            except TypeError:
                pass    
             
            ivd[v] = k     

        for fig_num in figlist:

            # get figure and drawn axes
            ax = plt.figure(fig_num).axes[0]
            xlab = ax.get_xlabel()
            ylab = ax.get_ylabel()
            
            # remove multi-compoent extension
            try:
                ext_x = xlab.split('[')[1]
            except IndexError:
                ext_x = ''
            else:
                ext_x = ext_x.split(']')[0]
            xlab = xlab.split('[')[0].strip()
            
            try:
                ext_y = ylab.split('[')[1]
            except IndexError:
                ext_y = ''
            else:
                ext_y = ext_y.split(']')[0]
            ylab = ylab.split('[')[0].strip()

            # convert from fancy label to simple label
            xlab = ivd.get(xlab, xlab)
            ylab = ivd.get(ylab, ylab)
            
            # add multi-componet stuff
            if ext_x: xlab += '_%s' % ext_x
            if ext_y: ylab += '_%s' % ext_y
                        
            # set new labels for drawing
            self.xaxis.set(xlab)
            self.yaxis.set(ylab)

            # draw new labels
            self.plt.active['param'] = fig_num
            self.draw_param()

            self.logger.debug('Updated figure %d (%s vs %s)', fig_num, ylab, xlab)

        # reset to old settings
        self.bfit.draw_style.set(current_style)
        self.xaxis.set(current_xlab)
        self.yaxis.set(current_ylab)
        self.plt.active['param'] = current_active
        plt.figure(current_active)

# =========================================================================== #
# =========================================================================== #
class fitline(object):
    """
        Instance variables

            bfit            pointer to top class
            dataline        pointer to dataline object in fetch_files_tab
            disable_entry_callback  disables copy of entry strings to
                                    dataline.bdfit parameter values
            lines           list of InputLine objects
            parent          pointer to parent object (frame)
            run_label       label for showing which run is selected
            run_label_title label for showing which run is selected
            fitframe        mainframe for this tab.
    """

    n_runs_max = 5      # number of runs before scrollbar appears
    collist = ['p0', 'blo', 'bhi', 'res', 'dres-', 'dres+', 'chi', 'fixed', 'shared']
    selected = 0        # index of selected run

    # ======================================================================= #
    def __init__(self, bfit, parent, dataline, row):
        """
            Inputs:
                bfit:       top level pointer
                parent:     pointer to parent frame object
                dataline:   fetch_files.dataline object corresponding to the
                                data we want to fit
                row:        grid position
        """

        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing fit line for run %d in row %d',
                          dataline.run, row)

        # initialize
        self.bfit = bfit
        self.parent = parent
        self.dataline = dataline
        self.row = row
        self.disable_entry_callback = False
        self.lines = []

        # get parent frame
        fitframe = ttk.Frame(self.parent, pad=(5, 0))

        frame_title = ttk.Frame(fitframe)

        # label for displyaing run number
        if type(self.dataline.bdfit.bd) is bdata:
            self.run_label = Label(frame_title,
                            text='[ %d - %d ]' % (self.dataline.run,
                                                  self.dataline.year),
                           bg=colors.foreground, fg=colors.background)

        elif type(self.dataline.bdfit.bd) is bmerged:
            runs = textwrap.wrap(str(self.dataline.run), 5)

            self.run_label = Label(frame_title,
                                text='[ %s ]' % ' + '.join(runs),
                                bg=colors.foreground, fg=colors.background)

        # title of run
        self.run_label_title = Label(frame_title,
                            text=self.dataline.bdfit.title,
                            justify='right', fg=colors.red)

        # Parameter input labels
        gui_param_button = ttk.Button(fitframe, text='Initial Value',
                        command=lambda : self.bfit.fit_files.do_gui_param(id=self.dataline.id),
                        pad=0)
        result_comp_button = ttk.Button(fitframe, text='Result',
                        command=self.draw_fn_composition, pad=0)

        c = 0
        ttk.Label(fitframe, text='Parameter').grid(     column=c, row=1, padx=5); c+=1
        gui_param_button.grid(                          column=c, row=1, padx=5, pady=2); c+=1
        ttk.Label(fitframe, text='Low Bound').grid(     column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='High Bound').grid(    column=c, row=1, padx=5); c+=1
        result_comp_button.grid(                        column=c, row=1, padx=5, pady=2, sticky=(E, W)); c+=1
        ttk.Label(fitframe, text='Error (-)').grid(     column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='Error (+)').grid(     column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='ChiSq').grid(         column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='Fixed').grid(         column=c, row=1, padx=5); c+=1
        ttk.Label(fitframe, text='Shared').grid(        column=c, row=1, padx=5); c+=1
        
        self.run_label.grid(column=0, row=0, padx=5, pady=5, sticky=W)
        self.run_label_title.grid(column=2, row=0, padx=5, pady=5, sticky=E)
        frame_title.grid(column=0, row=0, columnspan=c, sticky=(E, W))
        frame_title.columnconfigure(1, weight=1)

        # save frame
        self.fitframe = fitframe

        # resizing
        for i in range(c):
            self.fitframe.grid_columnconfigure(i, weight=1)

        # fill with initial parameters
        self.parlabels = []     # track all labels and inputs

    # ======================================================================= #
    def __del__(self):

        if hasattr(self, 'parlabels'):   del self.parlabels

        # kill buttons and frame
        try:
            for child in self.parent.winfo_children():
                child.destroy()
        except Exception:
            pass

        if hasattr(self, 'parentry'):    del self.parentry

    # ======================================================================= #
    def get_new_parameters(self):
        """
            Fetch initial parameters from fitter, set to data.

            plist: Dictionary of initial parameters {par_name:par_value}
        """
        
        run = self.dataline.id

        # get pointer to fit files object
        fit_files = self.bfit.fit_files
        fitter = fit_files.fitter
        ncomp = fit_files.n_component.get()
        fn_title = fit_files.fit_function_title.get()

        # get list of parameter names
        plist = list(fitter.gen_param_names(fn_title, ncomp))
        plist.sort()

        # check if we are using the fit results of the prior fit
        values_res = None
        res = self.bfit.data[run].fitpar['res']
        
        isfitted = any(res.values) # is this run fitted?
        
        if fit_files.set_prior_p0.get() and not isfitted:
            
            r = 0
            for rkey in self.bfit.data:
                data = self.bfit.data[rkey]
                
                isfitted = any(data.fitpar['res'].values) # is the latest run fitted?
                if isfitted and data.run > r:
                    r = data.run
                    values_res = data.fitpar
        
        # get calcuated initial values
        try:
            values = fitter.gen_init_par(fn_title, ncomp, self.bfit.data[run].bd,
                                    self.bfit.get_asym_mode(fit_files))
        except Exception as err:
            print(err)
            self.logger.exception(err)
            return tuple()
              
        # set p0 from old
        if values_res is not None:
            values['p0'] = values_res['res']
                                     
        # set to data
        self.bfit.data[run].set_fitpar(values)
        
        return tuple(plist)

    # ======================================================================= #
    def grid(self, row):
        """Re-grid a dataline object so that it is in order by run number"""
        self.row = row
        self.fitframe.grid(column=0, row=row, sticky=(W, N))
        self.fitframe.update_idletasks()

    # ======================================================================= #
    def degrid(self):
        """Remove displayed dataline object from file selection. """

        self.logger.debug('Degridding fitline for run %s', self.dataline.id)
        self.fitframe.grid_forget()
        self.fitframe.update_idletasks()

    # ======================================================================= #
    def draw_fn_composition(self):
        """
            Draw window with function components and total
        """

        self.logger.info('Drawing fit composition for run %s', self.dataline.id)

        # get top objects
        fit_files = self.bfit.fit_files
        bfit = self.bfit

        # get fit object
        bdfit = self.dataline.bdfit

        # get base function
        fn_name = fit_files.fit_function_title.get()

        # get number of components and parameter names
        ncomp = fit_files.n_component.get()
        pnames_single = fit_files.fitter.gen_param_names(fn_name, 1)
        pnames_combined = fit_files.fitter.gen_param_names(fn_name, ncomp)

        if '2' in bdfit.mode:
            fn_single = fit_files.fitter.get_fn(fn_name=fn_name, ncomp=1,
                            pulse_len=bdfit.pulse_s,
                            lifetime=bd.life[bfit.probe_species.get()])
            fn_combined = fit_files.fitter.get_fn(fn_name=fn_name, ncomp=ncomp,
                            pulse_len=bdfit.pulse_s,
                            lifetime=bd.life[bfit.probe_species.get()])
        else:
            fn_single = fit_files.fitter.get_fn(fn_name=fn_name, ncomp=1)
            fn_combined = fit_files.fitter.get_fn(fn_name=fn_name, ncomp=ncomp)

        # draw in redraw mode
        draw_mode = bfit.draw_style.get()
        bfit.draw_style.set('redraw')

        # draw the data
        bdfit.draw(bfit.get_asym_mode(fit_files), figstyle='fit', color='k')

        # get the fit results
        results = {par:bdfit.fitpar.loc[par, 'res'] for par in pnames_combined}

        # draw if ncomp is 1
        if ncomp == 1:
            bfit.draw_style.set('stack')
            bdfit.draw_fit('fit', unique=False, 
                           asym_mode=bfit.get_asym_mode(self.bfit.fit_files), 
                           label=fn_name)
            self.bfit.draw_style.set(draw_mode)
            return

        # draw baseline
        if 'baseline' in pnames_single:
            bfit.plt.axhline('fit', bdfit.id+'_base', results['baseline'], ls='--', zorder=6)

        # get x pts
        t, a, da = bdfit.asym(bfit.get_asym_mode(fit_files))
        fitx = np.linspace(min(t), max(t), fit_files.n_fitx_pts)

        # get x axis scaling
        if bdfit.mode in bfit.units:
            unit = bfit.units[bdfit.mode]
        else:
            fitxx = fitx

        # draw relative to peak 0
        if self.bfit.draw_rel_peak0.get():
            
            # get reference
            par = data.fitpar
            
            if 'peak_0' in par.index:   index = 'peak_0'
            elif 'mean_0' in par.index: index = 'mean_0'
            elif 'peak' in par.index:   index = 'peak'
            elif 'mean' in par.index:   index = 'mean'
            else:
                msg = "No 'peak' or 'mean' fit parameter found. Fit with" +\
                     " an appropriate function."
                self.logger.exception(msg)
                messagebox.error(msg)
                raise RuntimeError(msg)
            
            ref = par.loc[index, 'res']
            
            # do the shift
            fitxx = fitx-ref                    
            fitxx *= unit[0]
            xlabel = 'Frequency Shift (%s)' % unit[1]
            self.logger.info('Drawing as freq shift from peak_0')
        
        # ppm shift
        elif self.bfit.draw_ppm.get():
            
            # check div zero
            try:
                fitxx = 1e6*(fitx-self.bfit.ppm_reference)/self.bfit.ppm_reference
            except ZeroDivisionError as err:
                self.logger.exception(str(msg))
                messagebox.error(str(msg))
                raise err
            
            self.logger.info('Drawing as PPM shift with reference %s Hz', 
                             self.bfit.ppm_reference)
            xlabel = 'Frequency Shift (PPM)'
            
        else: 
            fitxx = fitx*unit[0]

        # draw the combined
        params = [results[name] for name in pnames_combined]

        bfit.plt.plot('fit', bdfit.id+'_comb', fitxx, fn_combined(fitx, *params),
                            unique=False, label='Combined', zorder=5)

        # draw each component
        for i in range(ncomp):

            # get parameters
            params = [results[single+'_%d'%i] \
                        for single in pnames_single if single != 'baseline']

            if 'baseline' in pnames_single:
                params.append(results['baseline'])

            # draw
            bfit.plt.plot('fit', bdfit.id+'_%d'%i, fitxx, fn_single(fitx, *params),
                            unique=False, ls='--', label='%s %d'%(fn_name, i), zorder=6)

        # plot legend
        bfit.plt.legend('fit')

        # reset to old draw mode
        bfit.draw_style.set(draw_mode)

    # ======================================================================= #
    def populate(self, force_modify=False):
        """
            Fill and grid new parameters. Reuse old fields if possible

            force_modify: if true, clear and reset parameter inputs.
        """

        # get list of parameters and initial values
        try:
            plist = self.get_new_parameters()
        except KeyError as err:
            return          # returns if no parameters found
        except RuntimeError as err:
            messagebox.showerror('RuntimeError', err)
            raise err from None

        self.logger.debug('Populating parameter list with %s', plist)
        
        # get data and frame
        fitframe = self.fitframe
        fitdat = self.dataline.bdfit
        
        # get needed number of lines
        n_lines_total = len(plist)
        n_lines_current = len(self.lines)
        n_lines_needed = n_lines_total - n_lines_current
        
        # drop unneeded lines
        if n_lines_needed < 0:
            
            unused = self.lines[n_lines_total:]
            for rem in unused:
                rem.degrid()
                del rem
            self.lines = self.lines[:n_lines_total]
            
        # add new lines
        elif n_lines_needed > 0:
            self.lines.extend([InputLine(fitframe, self.bfit, self) for i in range(n_lines_needed)])
        
        # reassign and regrid lines
        for i, line in enumerate(self.lines):
            line.grid(i+2)
            
        # drop old parameters
        fitdat.drop_unused_param(plist)
        
        # set initial parameters
        fitdat.fitpar.sort_index(inplace=True)
        param_values = fitdat.fitpar
        for i, k in enumerate(param_values.index):
            self.lines[i].assign_shared()
            self.lines[i].set(k, **param_values.loc[k].to_dict())

    # ======================================================================= #
    def show_fit_result(self):
        self.logger.debug('Showing fit result for run %s', self.dataline.id)

        # Set up variables
        displays = self.parentry

        try:
            data = self.dataline.bdfit
        except KeyError:
            return
        
        try:
            chi = data.chi
        except AttributeError:
            return

        # display
        for parname in displays.keys():
            disp = displays[parname]
            showstr = "%"+".%df" % self.bfit.rounding
            disp['res'][0].set(showstr % data.fitpar.loc[parname, 'res'])
            disp['dres-'][0].set(showstr % data.fitpar.loc[parname, 'dres-'])
            disp['dres+'][0].set(showstr % data.fitpar.loc[parname, 'dres+'])

            if 'chi' in disp.keys():
                disp['chi'][0].set('%.2f' % chi)
                if float(chi) > self.bfit.fit_files.chi_threshold:
                    disp['chi'][1]['readonlybackground']='red'
                else:
                    disp['chi'][1]['readonlybackground']=colors.readonly


