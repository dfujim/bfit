from bfit.gui.bfit import bfit, logger_name
from bfit import __version__
import logging, os, sys
from logging.handlers import RotatingFileHandler
import argparse, subprocess, requests, json
from textwrap import dedent
from pkg_resources import parse_version 

# check if maxOS
if sys.platform == 'darwin':
    os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

# run
if __name__ == '__main__':

    # command line switches ---------------------------------------------------
    parser = argparse.ArgumentParser(description=dedent("""\
        Run BNMR data viewer and fitter for online application."""), 
        formatter_class=argparse.RawTextHelpFormatter)
    
    # logging level
    parser.add_argument("-d", "--debug", 
                        help='Run in debug mode', 
                        dest='debug', 
                        action='store_true', 
                        default=False)

    # parse
    args = parser.parse_args()

    # Setup logging -----------------------------------------------------------
    logger = logging.getLogger(logger_name)

    # get log filename
    try:
        filename = os.path.join(os.environ['HOME'], '.bfit.log')
    except KeyError:
        filename = 'bfit.log'

    # make handler
    handler = RotatingFileHandler(filename, 
                                  mode='a', 
                                  maxBytes=100*1000, # 100 kB max
                                  backupCount=1)

    # get level and format for output string
    if args.debug:
        level = logging.DEBUG
        fmt = '%(asctime)s %(levelname)-8s %(module)s.%(funcName)s() [%(lineno)d] -- %(message)s'
    else:
        level = logging.INFO
        fmt = '%(asctime)s %(levelname)-8s %(module)s -- %(message)s'
    
    # set
    handler.setFormatter(logging.Formatter(fmt))
    handler.setLevel(level)

    logger.addHandler(handler)
    logger.setLevel(level)
    
    # testing
    testfn = None
    # ~ def testfn(self):
        # ~ self.fetch_files.run.set("40123, 40127")
        # ~ self.fetch_files.year.set(2012)
        # ~ self.fetch_files.get_data()
        # ~ self.fit_files.fit_function_title.set("QuadLorentz")
        # ~ self.fit_files.populate()
        # ~ self.notebook.select(2)
        # ~ self.fit_files.do_fit()
        # ~ import matplotlib.pyplot as plt
        # ~ plt.close('all')
        # ~ self.fit_files.do_add_param()
        
    # Check version (credit: https://github.com/alexmojaki/outdated) ----------
    try:
        latest_version = requests.get('https://pypi.python.org/pypi/bfit/json').text
        latest_version = json.loads(latest_version)['info']['version']
        latest_version2 = parse_version(latest_version)
        current_version = parse_version(str(__version__))
        
        if current_version < latest_version2: 
            messagebox.showinfo("Please update", 
                                "New version available!\n(%s)" % latest_version)
    except Exception:
        pass
    
    # start bfit --------------------------------------------------------------
    bfit(testfn)
    
