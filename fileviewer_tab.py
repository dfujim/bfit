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
        self.text = Text(view_frame,width=150,height=40,state='normal')
        self.text.grid(column=0,row=0)
        self.text.columnconfigure(0, weight=1)
        self.text.rowconfigure(0, weight=1)
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
        data = self.bfit.data[0]
        
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
                    '2h':'Alpha Tagging','2s':'Spin Echo'}
        
        key_order = ['Area','Run Mode','Title','Experimenters','Sample',
                    'Run Duration','Start','End']
        
        # fetch
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
            
        # get data: headers
        mode = mode_dict[data.mode]
        try:
            if data.ppg.rf_enable.mean:
                mode = "Hole Burning"
        except AttributeError:
            pass
        
        mins,sec = divmod(data.duration, 60)
        duration = "%dm %ds" % (mins,sec)
        
        data_dict =  {  "Area": data.area,
                        "Run Mode": mode,
                        "Title": data.title,
                        "Experimenters": data.experimenter,
                        "Sample": data.sample,
                        "Run Duration": duration,
                        "Start": data.start_date,
                        "End": data.end_date}
        
        # get data: temperature and fields
        try:
            temp = data.camp.smpl_read_A.mean
            temp_stdv = data.camp.smpl_read_A.std
            data_dict["Temperature"] = "%.2f +/- %.2f K" % (temp,temp_stdv)
            key_order.append('Temperature')
        except AttributeError:
            pass
        
        try: 
            field = np.around(data.camp.b_field.mean,3)
            data_dict['Magnetic Field'] = "%.3f T" % field
            key_order.append('Magnetic Field')
        except AttributeError:
            pass
            
        # get data: needle and cryolift position
        try:
            needle_set = np.around(data.camp.needle_set.mean,3)
            needle_read = np.around(data.camp.needle_read.mean,3)
            lift_set = np.around(data.camp.clift_set.mean,3)
            lift_read = np.around(data.camp.clift_read.mean,3)
            data_dict['Needle Setpoint'] = "%.3f turns" % needle_set
            data_dict['Needle Readback'] = "%.3f turns" % needle_read
            data_dict['Cryo Lift Setpoint'] = "%.3f mm" % lift_set
            data_dict['Cryo Lift Readback'] = "%.3f mm" % lift_read
            key_order.append('Needle Setpoint')
            key_order.append('Needle Readback')
            key_order.append('Cryo Lift Setpoint')
            key_order.append('Cryo Lift Readback')
        except AttributeError:
            pass
            
        # get data: biases 
        try:
            if 'nqr_bias' in data.epics.keys():
                bias =  data.epics.nqr_bias.mean/1000.
            elif 'nmr_bias_p' in data.epics.keys():
                bias =  data.epics.nmr_bias_p.mean
            
            data_dict["Platform Bias"] = "%.3f kV" % np.around(bias,3)
            key_order.append('Platform Bias')
        except UnboundLocalError:
            pass
        
        try:
            data_dict["BIAS15"] = "%.3f V" % np.around(data.epics.bias15.mean,3)
            key_order.append('BIAS15')
        except AttributeError:
            pass
        
        # get data: beam energy
        try: 
            init_bias = data.epics.itw_bias.mean
        except AttributeError:
            try:
                init_bias = data.epics.ite_bias.mean
            except AttributeError:
                pass
            
        try:
            data_dict["Initial Beam Energy"] = "%.3f keV" % \
                    np.around(init_bias/1000.,3)
            key_order.append('Initial Beam Energy')
        except UnboundLocalError:
            pass
        
        # Get final beam energy
        try: 
            data_dict['Beam Energy at Sample'] = "%.3f keV" % \
                    np.around(data.beam_kev(),3)
            key_order.append('Beam Energy at Sample')
        except AttributeError:
            pass
        
        # get data: SLR data
        try:
            dwell = int(data.ppg.dwelltime.mean)
            beamon = int(data.ppg.beam_on.mean)
            beamoff = int(data.ppg.beam_off.mean)
            data_dict['Dwell Time'] = "%d ms" % dwell
            data_dict['Beam On Dwell Time'] = "%d dwelltimes" % beamon
            data_dict['Beam Off Dwell Time'] = "%d dwelltimes" % beamoff
            
            key_order.append('Dwell Time')
            key_order.append('Beam On Dwell Time')
            key_order.append('Beam Off Dwell Time')
        except AttributeError:
            pass
        
        # get data: holeburning data
        try:
            if int(data.ppg.rf_enable.mean):
                rf_on = int(data.ppg.rf_on.mean)
                rf_delay = int(data.ppg.rf_on_delay.mean)
                freq = int(data.ppg.freq.mean)
                
                data_dict['RF On Duration'] = "%d dwelltimes" % rf_on
                data_dict['RF On Delay'] = "%d Hz" % rf_delay
                data_dict['Frequency'] = "%d Hz" % freq
                
                key_order.append('RF On Duration')
                key_order.append('RF On Delay')
                key_order.append('Frequency')
        except AttributeError:
            pass
        
        # get 1F specific data
        try:
            fmin = int(data.ppg.freq_start.mean)
            fmax = int(data.ppg.freq_stop.mean)
            df = int(data.ppg.freq_incr.mean)
            data_dict['Frequency Range'] = "[%d,%d] Hz" % (fmin,fmax)
            data_dict['Frequency Step'] = "%d Hz" % df
            
            key_order.append('Frequency Range')
            key_order.append('Frequency Step')
        except AttributeError:
            pass

        # rf dac
        if mode != 'SLR':
            try: 
                data_dict['rf_dac'] = "%d" % int(data.camp.rf_dac.mean)
                key_order.append('rf_dac')
            except AttributeError:
                pass
        
        # get Rb Cell specific data
        try:
            fmin = int(data.ppg.volt_start.mean)
            fmax = int(data.ppg.volt_stop.mean)
            df = int(data.ppg.volt_incr.mean)
            data_dict['Voltage Range'] = "[%d,%d] V" % (fmin,fmax)
            data_dict['Voltage Step'] = "%d V" % df
            
            key_order.append('Voltage Range')
            key_order.append('Voltage Step')
        except AttributeError:
            pass
        
        # set viewer string
        m = max(max(map(len, list(data_dict.keys()))) + 1,25)
        s = '\n'.join([k.rjust(m) + ': ' + data_dict[k]
                          for k in key_order])
        
        self.set_textbox_text(self.text,s)
        
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

