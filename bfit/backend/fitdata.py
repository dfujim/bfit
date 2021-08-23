# Data object for holding bdata and related file settings for drawing and 
# fitting. 
# Derek Fujimoto
# Nov 2018

from tkinter import *
from bdata import bdata, bmerged
from bfit.gui.calculator_nqr_B0 import current2field
from bfit.gui.calculator_nqr_B0_hh6 import current2field as current2field_hh6
from bfit import logger_name

from bfit.backend.raise_window import raise_window

import numpy as np
import pandas as pd

import bfit
import logging
import textwrap

# =========================================================================== #
# =========================================================================== #
class fitdata(object):
    """
        Hold bdata and related file settings for drawing and fitting in fetch 
        files tab and fit files tab. 
        
        Data Fields:
            
            bd:         bdata object for data and asymmetry (bdata)
            bfit:       pointer to top level parent object (bfit)
            bias:       platform bias in kV (float)
            bias_std:   platform bias in kV (float)
            check_state:(BooleanVar)  
            chi:        chisquared from fit (float)
            drawarg:    drawing arguments for errorbars (dict)
            field:      magnetic field in T (float)
            field_std:  magnetic field standard deviation in T (float)
            fitfn:      function (function pointer)
            fitfnname:  function (str)
            fitpar:     initial parameters {column:{parname:float}} and results
                        Columns are fit_files.fitinputtab.collist
            id:         key for unique idenfication (str)    
            label:      label for drawing (StringVar)
            mode:       run mode (str, ex: 1f)
            omit:       omit bins, 1f only (StringVar)
            parnames:   parameter names in the order needed by the fit function
            rebin:      rebin factor (IntVar)
            run:        run number (int)
            year:       run year (int)
              
    """
     
    # ======================================================================= #
    def __init__(self, bfit, bd):
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing run %d (%d).', bd.run, bd.year)
        
        # top level pointers
        self.bfit = bfit
        
        # bdata access
        self.bd = bd
        
        # input variables for tkinter
        self.rebin = IntVar()
        self.omit = StringVar()
        self.label = StringVar()
        self.check_state = BooleanVar()
        
        self.nbm = self.bfit.use_nbm
        
        self.rebin.set(1)
        self.omit.set('')
        self.label.set('')
        self.check_state.set(False)
        
        # key for IDing file 
        self.id = self.bfit.get_run_key(data=bd)
        
        # initialize fitpar with fitinputtab.collist
        self.fitpar = pd.DataFrame([], columns=['p0', 'blo', 'bhi', 'res', 
                                    'dres+', 'dres-', 'chi', 'fixed', 'shared'])
        
        # set area as upper
        self.area = self.area.upper()
        
        self.read()

    # ======================================================================= #
    def __getattr__(self, name):
        """Access bdata attributes in the case that fitdata doesn't have it."""
        try:
            return self.__dict__[name]
        except KeyError:
            return getattr(self.bd, name)

    # ======================================================================= #
    def asym(self, *args, **kwargs):
        
        deadtime = 0
        
        # check if deadtime corrections are needed
        if self.bfit.deadtime_switch.get():
            
            # check if corrections should be calculated for each run
            if self.bfit.deadtime_global.get():
                deadtime = self.bfit.deadtime
            else:
                deadtime = self.bd.get_deadtime(c=self.bfit.deadtime, fixed='c')
        
        # check for errors
        try:
            return self.bd.asym(*args, deadtime=deadtime, **kwargs)
        except Exception as err:
            messagebox.showerror(title=type(err).__name__, message=str(err))
            self.logger.exception(str(err))
            raise err from None

    # ======================================================================= #
    def draw(self, asym_type, figstyle='', **drawargs):
        """
            Draw the selected file
            
            bfit:       bfit object
            asym_type:  input for asymmetry calculation
            figstyle:   figure style. One of "data", "fit", or "param"
            drawargs:   passed to errorbar
        """
        
        self.logger.info('Drawing run %d (%d). mode: %s, rebin: %d, '+\
                     'asym_type: %s, style: %s, %s', 
                     self.run, 
                     self.year, 
                     self.mode, 
                     self.rebin.get(), 
                     asym_type, 
                     self.bfit.draw_style.get(), 
                     drawargs)
        
        # useful pointers
        bfit = self.bfit
        plt = self.bfit.plt
        rebin = self.rebin.get()
        omit = self.omit.get()
        
        # check omit values
        if omit == self.bfit.fetch_files.bin_remove_starter_line:
            omit = ''
        
        # convert asym type
        asym_type = self.bfit.asym_dict.get(asym_type, asym_type)
        
        # default label value
        if 'label' not in drawargs.keys():
            label = str(self.run)
        else:
            label = drawargs.pop('label', None)
            
        # set drawing style arguments
        for k in bfit.style:
            if k not in drawargs.keys():
                drawargs[k] = bfit.style[k]
        
        # get drawing style (ex: stack)
        draw_style = bfit.draw_style.get()
        
        # make new window
        if draw_style == 'new' or not plt.active[figstyle]:
            plt.figure(figstyle)
        elif draw_style == 'redraw':
            plt.clf(figstyle)
            
        ax = plt.gca(figstyle)
        
        # set axis offset
        try:
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
        except AttributeError:
            pass
        
        # get asymmetry: raw scans
        if asym_type == 'r' and '1' in self.mode:
            a = self.asym('raw', omit=self.omit.get(), 
                          hist_select=bfit.hist_select, 
                          nbm=bfit.use_nbm.get())
            x = np.arange(len(a.p[0]))
            idx_p = a.p[0]!=0
            idx_n = a.n[0]!=0
            
            xlabel = 'Bin'
            plt.errorbar(figstyle, self.id, x[idx_p], a.p[0][idx_p], a.p[1][idx_p], 
                    label=label+"($+$)", **drawargs)
            
            plt.errorbar(figstyle, self.id, x[idx_n], a.n[0][idx_n], a.n[1][idx_n], 
                    label=label+"($-$)", unique=False, **drawargs)
            
        # do 2e mode
        elif self.mode == '2e':
            
            # get asym
            a = self.asym(hist_select=bfit.hist_select)
        
            # draw
            if asym_type in ["raw_c", "raw_h", "raw_hs"]:
                
                # make 3D axes
                if type(plt.gcf(figstyle)) == type(None):   
                    plt.figure(figstyle)
                ax = plt.gcf(figstyle).add_subplot(111, projection='3d', 
                                  label=str(len(plt.gcf(figstyle).axes)))
                
                # get rid of bad draw options
                try:                del drawargs['capsize']
                except KeyError:    pass
                try:                del drawargs['elinewidth']
                except KeyError:    pass
                
                # for every frequency there is a multiple of times
                x = np.asarray([[t]*len(a.freq) for t in a.time])
                x = np.hstack(x)
                
                # for every time there is a set of frequencies
                y = np.asarray([a.freq for i in range(len(a.raw_c[0][0]))])*1e-6
                y = np.hstack(y)
                    
                # draw combined asym
                if asym_type == "raw_c":
                
                    z = a.raw_c[0].transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label, **drawargs)
                    
                elif asym_type == "raw_h":
                
                    z = a.raw_p[0].transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label+' ($+$)', **drawargs)
                    
                    
                    z = a.raw_n[0].transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label+' ($-$)', **drawargs)
                    
                elif asym_type == "raw_hs":
                
                    z = (a.raw_p[0]-a.raw_p[0][0]).transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label+' ($+$)', **drawargs)
                    
                    z = (a.raw_n[0]-a.raw_n[0][0]).transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label+' ($-$)', **drawargs)
                    
                # plot elements
                ax.set_xlabel('Time (ms)')
                ax.set_ylabel('Frequency (%s)' % bfit.units['2e'][1])
                
                if asym_type != "raw_hs":
                    ax.set_zlabel('Asymmetry')
                else:
                    ax.set_zlabel(r"Asym-Asym($\nu_{min}$)")
                ax.get_yaxis().get_major_formatter().set_useOffset(False)
                ax.get_xaxis().set_ticks(a.time)
            
            else:
                f = a.freq*bfit.units['2e'][0]
                if asym_type == 'sl_c':
                    plt.errorbar(figstyle, self.id, f, a.sl_c[0], a.sl_c[1], label=label, 
                                 **drawargs)
                    
                elif asym_type == 'dif_c':
                    plt.errorbar(figstyle, self.id, f, a.dif_c[0], a.dif_c[1], label=label, 
                                 **drawargs)
                    
                elif asym_type == 'sl_h':
                    plt.errorbar(figstyle, self.id, f, a.sl_p[0], a.sl_p[1], 
                                 label=label+' ($+$)', **drawargs)
                    
                                 
                    plt.errorbar(figstyle, self.id, f, a.sl_n[0], a.sl_n[1], 
                                 label=label+' ($-$)', **drawargs)
                    
                elif asym_type == 'dif_h':
                    plt.errorbar(figstyle, self.id, f, a.dif_p[0], a.dif_p[1], 
                                 label=label+' ($+$)', **drawargs)
                    
                    plt.errorbar(figstyle, self.id, f, a.dif_n[0], a.dif_n[1], 
                                 label=label+' ($-$)', **drawargs)
                    
                elif asym_type == 'sl_hs':
                    plt.errorbar(figstyle, self.id, f, a.sl_p[0]-a.sl_p[0][0], a.sl_p[1], 
                                 label=label+' ($+$)', **drawargs)
                    
                                 
                    plt.errorbar(figstyle, self.id, f, a.sl_n[0]-a.sl_n[0][0], a.sl_n[1], 
                                 label=label+' ($-$)', **drawargs)
                    
                    
                elif asym_type == 'dif_hs':
                    plt.errorbar(figstyle, self.id, f, a.dif_p[0]-a.dif_p[0][0], a.dif_p[1], 
                                 label=label+' ($+$)', **drawargs)
                    
                    
                    plt.errorbar(figstyle, self.id, f, a.dif_n[0]-a.dif_n[0][0], a.dif_n[1], 
                                 label=label+' ($-$)', **drawargs)
                    
                    
                plt.xlabel(figstyle, bfit.xlabel_dict[self.mode] % bfit.units['2e'][1])
                
                if '_hs' in asym_type:
                    plt.ylabel(figstyle, r"Asym-Asym($\nu_{min}$)")
                else:
                    plt.ylabel(figstyle, "Asymmetry")
            
        # get asymmetry: not raw scans, not 2e
        else:
            a = self.asym(omit=omit, 
                          rebin=rebin, 
                          hist_select=bfit.hist_select, 
                          nbm=bfit.use_nbm.get())
            
            # get x self
            if 'custom' in a.keys():
                x = a.custom
                unit = self.ppg.scan_var_histo_factor.units
                bfit.units[self.mode][1] = 'disable'
            else:
                x = a[bfit.x_tag[self.mode]]
                xlabel = bfit.xlabel_dict[self.mode]
            
            # get bfit-defined units
            if self.mode in bfit.units.keys() and bfit.units[self.mode][1].lower() \
                                                  not in ('default', 'disable'):                                                     
                unit = bfit.units[self.mode]
                xlabel = xlabel % unit[1]
            
            # get units for custom scans
            elif 'scan_var_histo_factor' in self.ppg.keys():
                unit = [self.ppg.scan_var_histo_factor.mean,
                        self.ppg.scan_var_histo_factor.units]     
                   
                # check custom name
                if 'customv_enable' in self.ppg.keys() and bool(self.ppg.customv_enable.mean):
                    xlabel = '%s (%s)' % (self.ppg.customv_name_write.units, unit[1])
                    
                # 1c runs custom name
                elif 'scan_device' in self.ppg.keys():
                    xlabel = '%s (%s)' % (self.ppg.scan_device.units, unit[1])
                
                # no name, use default
                else:
                    xlabel = xlabel % unit[1]
                        
            else:
                unit = [1, 'default']
                xlabel = xlabel % unit[1]
                        
            # unit conversions
            if self.mode in ('1n', '1w', '1c', '1d'): 
                x *= unit[0]
                
            elif self.mode in ('1f', '1x'): 
                
                # draw relative to peak 0
                if bfit.draw_rel_peak0.get():
                    
                    # get reference
                    par = self.fitpar
                    
                    if 'peak_0' in par.index:   index = 'peak_0'
                    elif 'mean_0' in par.index: index = 'mean_0'
                    elif 'peak' in par.index:   index = 'peak'
                    elif 'mean' in par.index:   index = 'mean'
                    else:
                        msg = "No 'peak' or 'mean' fit parameter found. Fit with" +\
                             " an appropriate function."
                        self.logger.exception(msg)
                        messagebox.showerror(msg)
                        raise RuntimeError(msg)
                    
                    ref = par.loc[index, 'res']
                    
                    # do the shift
                    x -= ref                    
                    x *= unit[0]
                    xlabel = 'Frequency Shift (%s)' % unit[1]
                    self.logger.info('Drawing as freq shift from peak_0')
                
                # ppm shift
                elif bfit.draw_ppm.get():
                    
                    # check div zero
                    try:
                        x = 1e6*(x-bfit.ppm_reference)/bfit.ppm_reference
                    except ZeroDivisionError as err:
                        self.logger.exception(str(msg))
                        messagebox.showerror(str(msg))
                        raise err
                    
                    self.logger.info('Drawing as PPM shift with reference %s Hz', 
                                     bfit.ppm_reference)
                    xlabel = 'Frequency Shift (PPM)'
                    
                else: 
                    x *= unit[0]
            
            # plot split helicities
            if asym_type == 'h':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
                
                # get average
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag_p], ap[tag_p], 
                                a.p[1][tag_p], label=label+" ($+$)", **drawargs)
                plt.errorbar(figstyle, self.id, x[tag_n], an[tag_n], 
                            a.n[1][tag_n], label=label+" ($-$)", unique=False, 
                            **drawargs)
                plt.axhline(figstyle, 'line', avg, color='k', linestyle='--')
                
            # plot positive helicity
            elif asym_type == 'p':
                
                # remove zero asym
                ap = a.p[0]
                tag = ap!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], ap[tag], a.p[1][tag], 
                                        label=label+" ($+$)", **drawargs)
                
            # plot negative helicity
            elif asym_type == 'n':
                
                # remove zero asym
                an = a.n[0]
                tag = an!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], an[tag], a.n[1][tag], 
                                        label=label+" ($-$)", **drawargs)
                
            # plot forward counter
            elif asym_type == 'fc':
                
                # remove zero asym
                af = a.f[0]
                tag = af!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], af[tag], a.f[1][tag], 
                                        label=label+" (Fwd)", **drawargs)
                
            # plot back counter
            elif asym_type == 'bc':
                                
                # remove zero asym
                ab = a.b[0]
                tag = ab!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], ab[tag], a.b[1][tag], 
                                        label=label+" (Bck)", **drawargs)
            
            # plot right counter
            elif asym_type == 'rc':
                
                # remove zero asym
                ar = a.r[0]
                tag = ar!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], ar[tag], a.r[1][tag], 
                                        label=label+" (Rgt)", **drawargs)
                
            # plot left counter
            elif asym_type == 'lc':
                                
                # remove zero asym
                al = a.l[0]
                tag = al!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], al[tag], a.l[1][tag], 
                                        label=label+" (Lft)", **drawargs)
                
            # plot split helicities, shifted by baseline
            elif asym_type == 'hs':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                dap = a.p[1]
                dan = a.n[1]
                tag_p = ap!=0
                tag_n = an!=0
                ap = ap[tag_p]
                an = an[tag_n]
                dap = dap[tag_p]
                dan = dan[tag_n]
                
                # subtract last 5 values
                end = np.average(ap[-5:], weights=1/dap[-5:]**2)
                dend = 1/np.sum(1/dap[-5:]**2)**0.5
                
                ap -= end
                dap = ((dend)**2+(dap)**2)**0.5
                
                end = np.average(an[-5:], weights=1/dan[-5:]**2)
                dend = 1/np.sum(1/dan[-5:]**2)**0.5
                
                an -= end
                dan = ((dend)**2+(dan)**2)**0.5
                
                plt.errorbar(figstyle, self.id, x[tag_p], ap, dap, 
                        label=label+" ($+$)", **drawargs)
                plt.errorbar(figstyle, self.id, x[tag_n], an, dan, 
                        label=label+" ($-$)", unique=False, **drawargs)
                
            # plot split helicities, flipped about the average
            elif asym_type == 'hm':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
            
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                
                plt.errorbar(figstyle, self.id, x[tag_p], a.p[0][tag_p], a.p[1][tag_p], 
                        label=label+" ($+$)", **drawargs)
                plt.errorbar(figstyle, self.id, x[tag_n], 2*avg-a.n[0][tag_n], a.n[1][tag_n], 
                        label=label+" ($-$)", unique=False, **drawargs)
                plt.axhline(figstyle, 'line', avg, color='k', linestyle='--')
            
            # plot split helicities, flipped about the average, find the largest 
            elif asym_type == 'hp':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                ap = ap[tag_p]
                an = an[tag_n]
                
                # get flipped asymmetries
                if np.mean(an) < avg:
                    an = 2*avg-an
                if np.mean(ap) < avg:
                    ap = 2*avg-ap
                
                # get largest asymmetry
                largest_p = max(ap)
                largest_n = max(an)
                
                if largest_p > largest_n:
                    largest = largest_p
                    vmax = x[np.where(ap==largest)[0][0]]
                else:
                    largest = largest_n
                    vmax = x[np.where(an==largest)[0][0]]
                
                # print
                print('Max asymmetry is %f at V = %f V' % (largest, vmax))
                
                # draw    
                plt.errorbar(figstyle, self.id, x[tag_p], ap, a.p[1][tag_p], 
                                  label=label+" ($+$)", **drawargs)
                plt.errorbar(figstyle, self.id, x[tag_n], an, a.n[1][tag_n], 
                                  label=label+" ($-$)", unique=False, **drawargs)
                plt.axhline(figstyle, 'line', largest, color='k', linestyle='--')
                plt.axvline(figstyle, 'line', vmax, color='k', linestyle='--', 
                                 unique=False)
                plt.text(figstyle, vmax+0.5, largest+0.0001, '%g V' % vmax, 
                              id='line', unique=False)
                
            # plot comined helicities
            elif asym_type == 'c':
                tag = a.c[0]!=0 # remove zero asym
                plt.errorbar(figstyle, self.id, x[tag], a.c[0][tag], a.c[1][tag], 
                                  label=label, **drawargs)
                         
            # plot combined helicities, shifted by baseline
            elif asym_type == 'cs':
                
                # remove zero asym
                ac = a.c[0]
                dac = a.c[1]
                tag = ac!=0
                ac = ac[tag]
                dac = dac[tag]
                
                # subtract last 5 values
                x = x[tag]
                
                if 'baseline' in self.fitpar['res'].keys() and bfit.norm_with_param.get():
                    shift = self.fitpar['res']['baseline']
                    dshift = np.sqrt(self.fitpar['dres+']['baseline']**2 + \
                                     self.fitpar['dres-']['baseline']**2)
                    asym_type += 'f'
                else:                
                    shift = np.average(ac[-5:], weights=1/dac[-5:]**2)
                    dshift = 1/np.sum(1/dac[-5:]**2)**0.5
                        
                ac -= shift
                dac = ((dshift)**2+(dac)**2)**0.5
                
                plt.errorbar(figstyle, self.id, x, ac, dac, label=label, **drawargs)
                
            # plot combined helicities, normalized by baseline 
            elif asym_type == 'cn1':
                
                # remove zero asym
                ac = a.c[0]
                dac = a.c[1]
                tag = ac!=0
                ac = ac[tag]
                dac = dac[tag]
                x = x[tag]
                
                # divide by last value or by baseline
                if 'baseline' in self.fitpar['res'].keys() and bfit.norm_with_param.get():
                    norm = self.fitpar['res']['baseline']
                    dnorm = np.sqrt(self.fitpar['dres+']['baseline']**2 + \
                                    self.fitpar['dres-']['baseline']**2)
                    asym_type += 'f'
                else:                
                    norm = np.average(ac[-5:], weights=1/dac[-5:]**2)
                    dnorm = 1/np.sum(1/dac[-5:]**2)**0.5
                        
                dac = ac/norm * ((dnorm/norm)**2 + (dac/ac)**2)**0.5
                ac /= norm
                plt.errorbar(figstyle, self.id, x, ac, dac, label=label, **drawargs)

            # plot combined helicities, normalized by initial asym
            elif asym_type == 'cn2':
                
                # remove zero asym
                ac = a.c[0]
                dac = a.c[1]
                tag = ac!=0
                ac = ac[tag]
                dac = dac[tag]
                x = x[tag]

                # divide by intial 
                if 'amp' in self.fitpar['res'].keys() and bfit.norm_with_param.get():
                    norm = self.fitpar['res']['amp']
                    dnorm = np.sqrt(self.fitpar['dres+']['amp']**2 + \
                                    self.fitpar['dres-']['amp']**2)
                    asym_type += 'f'
                else:
                    norm = ac[0]
                    dnorm = dac[0]

                dac = ac/norm * ((dnorm/norm)**2 + (dac/ac)**2)**0.5
                ac /= norm
                plt.errorbar(figstyle, self.id, x, ac, dac, label=label, **drawargs)
                
            # attempting to draw raw scans unlawfully
            elif asym_type == 'r':
                return
                
            # draw alpha diffusion
            elif asym_type == 'ad':
                a = self.asym('adif', rebin=rebin, hist_select=bfit.hist_select, 
                              nbm=bfit.use_nbm.get())
                plt.errorbar(figstyle, self.id, *a, label=label, **drawargs)
                plt.ylabel(figstyle, r'$N_\alpha/N_\beta$')
                
            # draw normalized alpha diffusion
            elif asym_type == 'adn':
                
                a = self.asym('adif', rebin=1, hist_select=bfit.hist_select, 
                              nbm=bfit.use_nbm.get())
                          
                # take mean of first few points
                idx = (a[0]<bfit.norm_alph_diff_time)*(~np.isnan(a[1]))
                a0 = np.average(a[1][idx], weights=1/a[2][idx]**2)
                
                # normalize
                a = self.asym('adif', rebin=rebin, hist_select=bfit.hist_select, 
                              nbm=bfit.use_nbm.get())
                a[1] /= a0
                a[2] /= a0
                
                plt.errorbar(figstyle, self.id, *a, label=label, **drawargs)
                plt.ylabel(figstyle, r'$N_\alpha/N_\beta$ (Normalized by t=0)')
                
            # draw alpha tagged runs
            elif asym_type in ['at_c', 'at_h', 'nat_c', 'nat_h']:
                
                a = self.asym('atag', rebin=rebin, hist_select=bfit.hist_select, 
                              nbm=bfit.use_nbm.get())
                t = a.time_s
                
                if asym_type == 'at_c':
                    plt.errorbar(figstyle, self.id, t, a.c_wiA[0], a.c_wiA[1], 
                                 label=label+r" $\alpha$", **drawargs)
                    
                elif asym_type == 'nat_c':
                    plt.errorbar(figstyle, self.id, t, a.c_noA[0], a.c_noA[1], 
                                 label=label+r" !$\alpha$", **drawargs)
                    
                elif asym_type == 'at_h':
                    plt.errorbar(figstyle, self.id, t, a.p_wiA[0], a.p_wiA[1], 
                                 label=label+r" $\alpha$ ($+$)", **drawargs)
                    
                    plt.errorbar(figstyle, self.id, t, a.n_wiA[0], a.n_wiA[1], 
                                 label=label+r" $\alpha$ ($-$)", **drawargs)
                    
                elif asym_type == 'nat_h':
                    plt.errorbar(figstyle, self.id, t, a.p_noA[0], a.p_noA[1], 
                                 label=label+r" !$\alpha$ ($+$)", **drawargs)
                    
                    plt.errorbar(figstyle, self.id, t, a.n_noA[0], a.n_noA[1], 
                                 label=label+r" !$\alpha$ ($-$)", **drawargs)
                    
            # draw raw histograms
            elif asym_type == 'rhist':
                
                # get the histograms 
                hist = self.hist
                
                # draw
                keylist = ('F+', 'F-', 'B+', 'B-', 'L+', 'R+', 'L-', 'R-', 
                             'NBMF+', 'NBMF-', 'NBMB+', 'NBMB-', 'AL0+', 'AL0-')
                for i, h in enumerate(keylist):
                    
                    # get bins
                    try:
                        x = np.arange(len(hist[h].data))
                    except KeyError:
                        continue
                    
                    # check for non-empty histograms, then draw
                    if np.mean(hist[h].data) > 0:                        
                        plt.plot(figstyle, self.id, x, hist[h].data, label=h, 
                                        unique=not bool(i))
                        
                plt.ylabel(figstyle, bfit.ylabel_dict[asym_type])
                plt.xlabel(figstyle, 'Bin')
                            
            # unknown run type
            else:
                raise RuntimeError("Unknown draw style")
                    
        # plot elements
        if self.mode != '2e' and asym_type != 'rhist':
            plt.xlabel(figstyle, xlabel)
            
            label = bfit.ylabel_dict.get(asym_type, "Asymmetry")
            if bfit.use_nbm.get():              label = 'NBM ' + label    
            plt.ylabel(figstyle, label)    
            
        plt.tight_layout(figstyle)
        plt.legend(figstyle)
        
        # bring window to front
        if figstyle != 'periodic':
            raise_window()   
            
        self.logger.debug('Drawing success.')

    # ======================================================================= #
    @property
    def beam_kev(self): 
        try:
            return self.bd.beam_keV
        except AttributeError:
            return np.nan
    
    @property
    def beam_kev_err(self): 
        try:
            return self.bd.beam_keV_err
        except AttributeError:
            return np.nan
        
    # ======================================================================= #
    def drop_unused_param(self, parnames):
        """
            Check self.fitpar for parameters not in list of parnames. Drop them.
        """
        unused = [p for p in self.fitpar.index if p not in parnames]
        self.fitpar = self.fitpar.drop(unused, axis='index')
    
    # ======================================================================= #
    def get_temperature(self, channel='A'):
        """
            Get the temperature of the run.
            Return (T, std T)
        """
        
        try:
            if channel == 'A':
                T = self.bd.camp['smpl_read_A'].mean
                dT = self.bd.camp['smpl_read_A'].std
            elif channel == 'B':
                T = self.bd.camp['smpl_read_B'].mean
                dT = self.bd.camp['smpl_read_B'].std
            elif channel == '(A+B)/2':
                Ta = self.bd.camp['smpl_read_A'].mean
                Tb = self.bd.camp['smpl_read_B'].mean
                dTa = self.bd.camp['smpl_read_A'].std
                dTb = self.bd.camp['smpl_read_B'].std
                
                T = (Ta+Tb)/2
                dT = ((dTa**2+dTb**2)**0.5)/2
            else:
                raise AttributeError("Missing required temperature channel.")
        
        except KeyError:
            T = np.nan
            dT = np.nan
        
        return (T, dT)
        
    # ======================================================================= #
    def read(self):
        """Read data file"""
        
        # bdata access
        if type(self.bd) is bdata:
            
            # load real run
            try:
                self.bd = bdata(self.run, self.year)
                
            # load test run
            except ValueError:
                self.bd = bdata(0, filename = self.bfit.fileviewer.filename)
                
        elif type(self.bd) is bmerged:
            years = list(map(int, textwrap.wrap(str(self.year), 4)))
            runs = list(map(int, textwrap.wrap(str(self.run), 5)))
            self.bd = bmerged([bdata(r, y) for r, y in zip(runs, years)])
                
        # set temperature 
        try:
            self.temperature = temperature_class(*self.get_temperature(self.bfit.thermo_channel.get()))
        except AttributeError as err:
            self.logger.exception(err)
            try:
                self.temperature = self.bd.camp.oven_readC
            except AttributeError:
                self.logger.exception('Thermometer oven_readC not found')
                self.temperature = -1111
        
        # field
        try:
            if self.area == 'BNMR':
                self.field = self.bd.camp.b_field.mean
                self.field_std = self.bd.camp.b_field.std
            else:
                
                if hasattr(self.bd.epics, 'hh6_current'):
                    self.field = current2field_hh6(self.bd.epics.hh6_current.mean)*1e-4
                    self.field_std = current2field_hh6(self.bd.epics.hh6_current.std)*1e-4
                else:
                    self.field = current2field(self.bd.epics.hh_current.mean)*1e-4
                    self.field_std = current2field(self.bd.epics.hh_current.std)*1e-4
                    
        except AttributeError:
            self.logger.exception('Field not found')
            self.field = np.nan
            self.field_std = np.nan
            
        # bias
        try:
            if self.area == 'BNMR': 
                self.bias = self.bd.epics.nmr_bias.mean
                self.bias_std = self.bd.epics.nmr_bias.std
            else:
                self.bias = self.bd.epics.nqr_bias.mean/1000.
                self.bias_std = self.bd.epics.nqr_bias.std/1000.
        except AttributeError:
            self.logger.exception('Bias not found')
            self.bias = np.nan
            
        # set area as upper
        self.area = self.area.upper()
        
    # ======================================================================= #
    def set_fitpar(self, values):
        """Set fitting initial parameters
        values: output of routine gen_init_par: DataFrame:            
                columns: [p0, blo, bhi, fixed]
                index: parameter names
        """
    
        self.parnames = values.index.values
    
        for v in self.parnames:
            for c in values.columns:
                self.fitpar.loc[v, c] = values.loc[v, c]
                
        self.logger.debug('Fit initial parameters set to %s', self.fitpar)

    # ======================================================================= #
    def set_fitresult(self, values):
        """
            Set fit results. Values is output of fitting routine. 
            
            values: {fn: function handle, 
                     'results': DataFrame of fit results,
                     'gchi': global chi2}
                     
            values['results']: 
                columns: [res, dres+, dres-, chi, fixed, shared]
                index: parameter names
        """
        
        # set function
        self.fitfn = values['fn']
        
        # get data frame
        df = values['results']
        
        # set parameter names
        self.parnames = df.index.values
        
        # set chi
        self.chi = df['chi'].values[0]
        
        # set parameters
        for v in self.parnames:
            for c in df.columns:
                self.fitpar.loc[v, c] = df.loc[v, c]
        self.logger.debug('Setting fit results to %s', self.fitpar)
    
# ========================================================================== #
class temperature_class(object):
    """
        Emulate storage container for camp variable smpl_read_%
    """
    
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std
    
