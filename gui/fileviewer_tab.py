# File viewer tab for bfit
# Derek Fujimoto
# Nov 2017

from tkinter import *
from tkinter import ttk
import numpy as np
import sys,os,datetime,time
from bdata import bdata
import matplotlib.pyplot as plt
from multiprocessing import Process, Pipe

__doc__ = """
    View file contents tab.
    
    To-do:
        2e mode viewing
        NBM viewing
        cumulative count viewing
    """

# =========================================================================== #
class fileviewer(object):
    """
        Data fields:
            year: year of exp
            runn: run number
            text: Text widget for displaying run information
            bfit: bfit object
            fig_list: list of figures
            asym_type: drawing style
            is_updating: True if update draw
            data: bdata object for drawing
    """
    
    asym_dict = {"Combined Helicity":'c',"Split Helicity":'h',"Raw Scans":'r'}
    asym_dict_keys = ("Combined Helicity","Split Helicity","Raw Scans")
    default_asym_key = "Combined Helicity"
    default_export_filename = "%d_%d.csv" # year_run.csv
    
    # ======================================================================= #
    def __init__(self,file_tab,bfit):
        """ Position tab tkinter elements"""
        
        # year and filenumber entry ------------------------------------------
        entry_frame = ttk.Frame(file_tab,borderwidth=1)
        self.year = StringVar()
        self.runn = StringVar()
        self.rebin = IntVar()
        self.bfit = bfit
        
        self.year.set(datetime.datetime.now().year)
        self.rebin.set(1)
        
        entry_year = ttk.Entry(entry_frame,\
                textvariable=self.year,width=5)
        self.entry_runn = ttk.Entry(entry_frame,\
                textvariable=self.runn,width=7)
        
        # fetch button
        fetch = ttk.Button(entry_frame,text='Fetch',command=self.get_data)
            
        # draw button
        draw = ttk.Button(entry_frame,text='Draw',command=self.draw)
        
        # grid and labels
        entry_frame.grid(column=0,row=0,sticky=N)
        ttk.Label(entry_frame,text="Year:").grid(column=0,row=0,sticky=E)
        entry_year.grid(column=1,row=0,sticky=E)
        ttk.Label(entry_frame,text="Run Number:").grid(column=2,row=0,sticky=E)
        self.entry_runn.grid(column=3,row=0,sticky=E)
        fetch.grid(column=4,row=0,sticky=E)
        draw.grid(column=5,row=0,sticky=E)
        
        # padding 
        for child in entry_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        # viewer frame -------------------------------------------------------
        view_frame = ttk.Frame(file_tab,borderwidth=2)
        
        self.text_nw = Text(view_frame,width=75,height=20,state='normal')
        self.text_ne = Text(view_frame,width=75,height=20,state='normal')
        self.text_sw = Text(view_frame,width=75,height=20,state='normal')
        self.text_se = Text(view_frame,width=75,height=20,state='normal')
        
        ttk.Label(view_frame,text="Run Info").grid(column=0,row=0,sticky=N)
        ttk.Label(view_frame,text="PPG Parameters").grid(column=1,row=0,sticky=N)
        ttk.Label(view_frame,text="Camp").grid(column=0,row=2,sticky=N)
        ttk.Label(view_frame,text="EPICS").grid(column=1,row=2,sticky=N)
        
        self.text_nw.grid(column=0,row=1,sticky=(N,W,E,S))
        self.text_ne.grid(column=1,row=1,sticky=(N,W,E,S))
        self.text_sw.grid(column=0,row=3,sticky=(N,W,E,S))
        self.text_se.grid(column=1,row=3,sticky=(N,W,E,S))
        
        view_frame.grid(column=0,row=1)
        
        # details frame: stuff at the bottom ----------------------------------
        details_frame = ttk.Frame(file_tab)
        entry_rebin = Spinbox(details_frame,from_=1,to=100,width=3,\
                textvariable=self.rebin)
        
        # update check box
        self.is_updating = BooleanVar()
        self.is_updating.set(False)
        update_box = Checkbutton(details_frame,text='Periodic Redraw',
                command=self.update,variable=self.is_updating,onvalue=True,
                offvalue=False,state=DISABLED)

        # asymmetry type combobox
        self.asym_type = StringVar()
        self.asym_type.set(self.default_asym_key)
        entry_asym_type = ttk.Combobox(details_frame,\
                textvariable=self.asym_type,state='readonly',width=15)
        entry_asym_type['values'] = self.asym_dict_keys
                
        # gridding
        ttk.Label(details_frame,text="Rebin:").grid(column=0,row=0,sticky=E)
        entry_rebin.grid(column=1,row=0,sticky=E)
        entry_asym_type.grid(column=2,row=0,sticky=E)
        update_box.grid(column=3,row=0,sticky=E)
        details_frame.grid(column=0,row=2,sticky=N)
        
        # padding 
        for child in details_frame.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
            
    # ======================================================================= #
    def __del__(self):
        pass
        
    # ======================================================================= #
    def draw(self):
        """Get data then draw."""
        if self.get_data():
            self.bfit.draw(self.data,\
                    self.asym_dict[self.asym_type.get()],rebin=self.rebin.get())
    
    # ======================================================================= #
    def export(self):
        """Export data as csv"""
        
        # get data
        if not self.get_data():
            return
        data = self.data
        
        # get filename 
        filename = filedialog.asksaveasfilename(
                initialfile=self.default_export_filename%(data.year,data.run))
        
        # write to file
        self.bfit.export(data,filename)
    
    # ======================================================================= #
    def get_data(self):
        """Display data and send bdata object to bfit draw list. 
        Return True on success, false on Failure
        """
        
        # settings
        mode_dict = {"20":"SLR","1f":"1F","1n":"Rb Cell Scan",
                    '2h':'Alpha Tagging','2s':'Spin Echo','2e':'2e'}
        
        # fetch data file
        try:
            year = int(self.year.get())
            run = int(self.runn.get())
        except ValueError:
            self.set_textbox_text(self.text,'Input must be integer valued')
            return False
        
        try: 
            data = bdata(run,year=year)
        except ValueError:
            self.set_textbox_text(self.text,'File read failed')
            return False
        except RuntimeError:
            self.set_textbox_text(self.text,'File does not exist.')
            return False
        
        # NE -----------------------------------------------------------------
        
        # get data: headers
        mode = mode_dict[data.mode]
        try:
            if data.ppg.rf_enable.mean:
                mode = "Hole Burning"
        except AttributeError:
            pass
        
        mins,sec = divmod(data.duration, 60)
        duration = "%dm %ds" % (mins,sec)
        
        # set dictionary
        data_nw =  {"Area": data.area,
                    "Run Mode": mode,
                    "Title": data.title,
                    "Experimenters": data.experimenter,
                    "Sample": data.sample,
                    "Run Duration": duration,
                    "Start": data.start_date,
                    "End": data.end_date}
        
        # set key order 
        key_order_nw = ['Area','Run Mode','Title','Experimenters','Sample',
                        'Run Duration','Start','End']
        
        # SW -----------------------------------------------------------------
        data_sw = {}
        key_order_sw = []
                        
        # get data: temperature and fields
        try:
            temp = data.camp.smpl_read_A.mean
            temp_stdv = data.camp.smpl_read_A.std
            data_sw["Temperature"] = "%.2f +/- %.2f K" % (temp,temp_stdv)
            key_order_sw.append('Temperature')
        except AttributeError:
            pass
        
        try: 
            field = np.around(data.camp.b_field.mean,3)
            data_sw['Magnetic Field'] = "%.3f T" % field
            key_order_sw.append('Magnetic Field')
        except AttributeError:
            pass
            
        # get data: needle and cryolift position
        try:
            needle_set = np.around(data.camp.needle_set.mean,3)
            needle_read = np.around(data.camp.needle_read.mean,3)
            lift_set = np.around(data.camp.clift_set.mean,3)
            lift_read = np.around(data.camp.clift_read.mean,3)
            data_sw['Needle Setpoint'] = "%.3f turns" % needle_set
            data_sw['Needle Readback'] = "%.3f turns" % needle_read
            data_sw['Cryo Lift Setpoint'] = "%.3f mm" % lift_set
            data_sw['Cryo Lift Readback'] = "%.3f mm" % lift_read
            key_order_sw.append('Needle Setpoint')
            key_order_sw.append('Needle Readback')
            key_order_sw.append('Cryo Lift Setpoint')
            key_order_sw.append('Cryo Lift Readback')
        except AttributeError:
            pass
            
        # rf dac
        if mode != 'SLR':
            try: 
                data_sw['rf_dac'] = "%d" % int(data.camp.rf_dac.mean)
                key_order_sw.append('rf_dac')
            except AttributeError:
                pass
            
        # SE -----------------------------------------------------------------
        data_se = {}
        key_order_se = []
            
        # get data: biases 
        try:
            if 'nqr_bias' in data.epics.keys():
                bias =  data.epics.nqr_bias.mean/1000.
            elif 'nmr_bias' in data.epics.keys():
                bias =  data.epics.nmr_bias.mean
            
            data_se["Platform Bias"] = "%.3f kV" % np.around(bias,3)
            key_order_se.append("Platform Bias")
            
        except UnboundLocalError:
            pass
        
        try:
            data_se["BIAS15"] = "%.3f V" % np.around(data.epics.bias15.mean,3)
            key_order_se.append('BIAS15')
        except AttributeError:
            pass
        
        # get data: beam energy
        try: 
            init_bias = data.epics.target_bias.mean
        except AttributeError:
            try:
                init_bias = data.epics.target_bias.mean
            except AttributeError:
                pass
            
        try:
            data_se["Initial Beam Energy"] = "%.3f keV" % \
                    np.around(init_bias/1000.,3)
            key_order_se.append('Initial Beam Energy')
        except UnboundLocalError:
            pass
        
        # Get final beam energy
        try: 
            data_se['Implantation Energy'] = "%.3f keV" % \
                    np.around(data.beam_kev(),3)
            key_order_se.append('Implantation Energy')
        except AttributeError:
            pass
        
        # NE -----------------------------------------------------------------
        data_ne = {}
        key_order_ne = []
        
        # get data: SLR data
        try:
            dwell = int(data.ppg.dwelltime.mean)
            beamon = int(data.ppg.beam_on.mean)
            beamoff = int(data.ppg.beam_off.mean)
            data_ne['Dwell Time'] = "%d ms" % dwell
            data_ne['Beam On Dwell Time'] = "%d dwelltimes" % beamon
            data_ne['Beam Off Dwell Time'] = "%d dwelltimes" % beamoff
            
            key_order_ne.append('Dwell Time')
            key_order_ne.append('Beam On Dwell Time')
            key_order_ne.append('Beam Off Dwell Time')
        except AttributeError:
            pass
        
        # get data: holeburning data
        try:
            if int(data.ppg.rf_enable.mean):
                rf_on = int(data.ppg.rf_on.mean)
                rf_delay = int(data.ppg.rf_on_delay.mean)
                freq = int(data.ppg.freq.mean)
                
                data_ne['RF On Duration'] = "%d dwelltimes" % rf_on
                data_ne['RF On Delay'] = "%d Hz" % rf_delay
                data_ne['Frequency'] = "%d Hz" % freq
                
                key_order_ne.append('RF On Duration')
                key_order_ne.append('RF On Delay')
                key_order_ne.append('Frequency')
        except AttributeError:
            pass
        
        # get 1F specific data
        try:
            fmin = int(data.ppg.freq_start.mean)
            fmax = int(data.ppg.freq_stop.mean)
            df = int(data.ppg.freq_incr.mean)
            data_ne['Frequency Range'] = "[%d,%d] Hz" % (fmin,fmax)
            data_ne['Frequency Step'] = "%d Hz" % df
            
            key_order_ne.append('Frequency Range')
            key_order_ne.append('Frequency Step')
        except AttributeError:
            pass
        
        # get Rb Cell specific data
        try:
            fmin = int(data.ppg.volt_start.mean)
            fmax = int(data.ppg.volt_stop.mean)
            df = int(data.ppg.volt_incr.mean)
            data_ne['Voltage Range'] = "[%d,%d] V" % (fmin,fmax)
            data_ne['Voltage Step'] = "%d V" % df
            
            key_order_ne.append('Voltage Range')
            key_order_ne.append('Voltage Step')
        except AttributeError:
            pass
        
        # set viewer string
        def set_str(data_dict,key_order,txtbox):
        
            m = max(max(map(len, list(data_dict.keys()))) + 1,5)
            s = '\n'.join([k.rjust(m) + ': ' + data_dict[k] for k in key_order])
            self.set_textbox_text(txtbox,s)
        
        set_str(data_nw,key_order_nw,self.text_nw)
        set_str(data_ne,key_order_ne,self.text_ne)
        set_str(data_sw,key_order_sw,self.text_sw)
        set_str(data_se,key_order_se,self.text_se)
        
        # set data field
        self.data = data
        
        return True
   
    # ======================================================================= #
    def set_textbox_text(self,textbox,text):
        """Set the text in a tkinter Text widget"""
        
        #~ textbox['state'] = 'normal'
        textbox.delete('1.0',END)
        textbox.insert('1.0',text)
        #~ textbox['state'] = 'disabled'
    
    # ======================================================================= #
    def update(self):
        pass
# =========================================================================== #

