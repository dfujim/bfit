# Search for runs based on some parameters
# Derek Fujimoto
# Sep 2024

from bdata import bdata
import numpy as np
import mudpy as mp
import pandas as pd

class searchable_bdata(bdata):

    def get_attribute(self, parname):
        """Get attribute of the bdata object to search

        Args:
            parname (str): name of parameter
        Returns:
            float|str: corresponding to that parameters value
        """

        # get value
        val = getattr(self, parname)

        if type(val) is mp.mvar.mvar:
            return val.mean
        else:
            return val

class database(object):

    def __init__(self, runs=None, years=None):
        """Create object with searchable parameters in order to find runs

        Args:
            runs (iterable): list of runs to look into
            years (iterable): list of years to look into
        """

        # get the data
        if runs is not None and years is not None:
            self.data = []
            for r in runs:
                for y in years:
                    try:
                        self.data.append(searchable_bdata(r, y))
                    except RuntimeError:
                        pass
            self.data = np.array(self.data)

    def get_runs(self):
        """Return a dataframe of runs and years for all entries in the database"""

        runyear = np.zeros((len(self.data), 2), dtype=int)

        for i, d in enumerate(self.data):
            runyear[i, 0] = d.run
            runyear[i, 1] = d.year
        return runyear
        # return pd.DataFrame({'run':runyear[:,0], 'year':runyear[:,1]}, dtype=int)

    def print_par(self, parname):
        for d in self.data:
            val = getattr(d, parname)
            print(f'{d.year}  {d.run}  {val}')

    def search(self, parname, searchterm):
        """Do the search.

        Args:
            parname (str): name of parameter to search through
            low (float): parameter must be larger than low
            high (float): parameter must be smaller than high
            substr (str): for string searches, this string must be in parameter

        Returns:
            A copy of this object with a smaller database size
        """

        # get the search term
        low = high = substr = None

        if type(searchterm) is str:
            substr = searchterm

        elif type(searchterm) in (np.ndarray, list, tuple) and len(searchterm) == 2:
            low, high = searchterm

        else:
            raise RuntimeError('bad input')

        # get the parameter
        values = np.array([b.get_attribute(parname) for b in self.data])

        # index of those that satisfy
        idx = np.full(len(values), True)
        if low is not None:
            idx *= values > low

        if high is not None:
            idx *= values < high

        if substr is not None:
            idx = np.array([substr in v for v in values])

        # get those values
        data = self.data[idx]

        # make new object
        obj = database()
        obj.data = data

        return obj
