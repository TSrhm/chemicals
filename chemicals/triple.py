# -*- coding: utf-8 -*-
'''Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2016, 2017, 2018, 2019 Caleb Bell <Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

__all__ = ['Tt_methods', 'Tt', 'Pt_methods', 'Pt']

import os
from chemicals.utils import PY37
from chemicals.phase_change import Tm
from chemicals.data_reader import (register_df_source,
                                   data_source,
                                   retrieve_from_df_dict,
                                   retrieve_any_from_df_dict,
                                   list_available_methods_from_df_dict)


# %% Register data sources and lazy load them
folder = os.path.join(os.path.dirname(__file__), 'Triple Properties')
register_df_source(folder, 'Staveley 1981.tsv')

STAVELEY = 'STAVELEY'
MELTING = 'MELTING'

_triple_data_loaded = False
def _load_triple_data():
    global triple_data_Staveley, _triple_data_loaded, Tt_sources, Pt_sources
    triple_data_Staveley = data_source('Staveley 1981.tsv')
    _triple_data_loaded = True
    Tt_sources = {
        STAVELEY: triple_data_Staveley,
    }
    Pt_sources = Tt_sources.copy()

if PY37:
    def __getattr__(name):
        if name in ('triple_data_Staveley', 'Tt_sources', 'Pt_sources'):
            _load_triple_data()
            return globals()[name]
        raise AttributeError("module %s has no attribute %s" %(__name__, name))
else:
    _load_triple_data()

Tt_methods = (STAVELEY, MELTING)

def Tt(CASRN, get_methods=False, method=None):
    r'''This function handles the retrieval of a chemical's triple temperature.
    Lookup is based on CASRNs. Will automatically select a data source to use
    if no method is provided; returns None if the data is not available.

    Returns data from [1]_, or a chemical's melting point if available.

    Parameters
    ----------
    CASRN : string
        CASRN [-]

    Returns
    -------
    Tt : float
        Triple point temperature, [K]
    methods : list, only returned if get_methods == True
        List of methods which can be used to obtain Tt with the
        given inputs

    Other Parameters
    ----------------
    method : string, optional
        A string for the method name to use, as defined by constants in
        Tt_methods
    get_methods : bool, optional
        If True, function will determine which methods can be used to obtain
        the Tt for the desired chemical, and will return methods
        instead of the Tt

    Notes
    -----
    Median difference between melting points and triple points is 0.02 K.
    Accordingly, this should be more than good enough for engineering
    applications.

    Temperatures are on the ITS-68 scale.

    Examples
    --------
    Ammonia

    >>> Tt('7664-41-7')
    195.48

    References
    ----------
    .. [1] Staveley, L. A. K., L. Q. Lobo, and J. C. G. Calado. "Triple-Points
       of Low Melting Substances and Their Use in Cryogenic Work." Cryogenics
       21, no. 3 (March 1981): 131-144. doi:10.1016/0011-2275(81)90264-2.
    '''
    if not _triple_data_loaded: _load_triple_data()
    if get_methods:
        methods = list_available_methods_from_df_dict(Tt_sources, CASRN, 'Tt68')
        if Tm(CASRN): methods.append(MELTING)
        return methods
    elif method:
        if method == MELTING:
            return Tm(CASRN)
        else:
            return retrieve_from_df_dict(Tt_sources, CASRN, 'Tt68', method) 
    else:
        Tt = retrieve_any_from_df_dict(Tt_sources, CASRN, 'Tt68') 
        if Tt: return Tt
        return Tm(CASRN)    
triple_point_temperature = Tt

Pt_methods = (STAVELEY,)

def Pt(CASRN, get_methods=False, method=None):
    r'''This function handles the retrieval of a chemical's triple pressure.
    Lookup is based on CASRNs. Will automatically select a data source to use
    if no method is provided; returns None if the data is not available.

    Returns data from [1]_ only. 
    
    This function doe snot implement it but it is also possible to calculate 
    the vapor pressure at the triple temperature from a vapor pressure
    correlation, if data is available; note most Antoine-type correlations do
    not extrapolate well to this low of a pressure.

    Parameters
    ----------
    CASRN : string
        CASRN [-]

    Returns
    -------
    Pt : float
        Triple point pressure, [Pa]
    methods : list, only returned if get_methods == True
        List of methods which can be used to obtain Pt with the
        given inputs

    Other Parameters
    ----------------
    method : string, optional
        A string for the method name to use, as defined by constants in
        Pt_methods
    get_methods : bool, optional
        If True, function will determine which methods can be used to obtain
        the Pt for the desired chemical, and will return methods
        instead of the Pt

    Notes
    -----

    Examples
    --------
    Ammonia

    >>> Pt('7664-41-7')
    6079.5

    References
    ----------
    .. [1] Staveley, L. A. K., L. Q. Lobo, and J. C. G. Calado. "Triple-Points
       of Low Melting Substances and Their Use in Cryogenic Work." Cryogenics
       21, no. 3 (March 1981): 131-144. doi:10.1016/0011-2275(81)90264-2.
    '''
    if not _triple_data_loaded: _load_triple_data()
    if get_methods:
        methods = list_available_methods_from_df_dict(Pt_sources, CASRN, 'Pt')
        return methods
    elif method:
        return retrieve_from_df_dict(Pt_sources, CASRN, 'Pt', method) 
    else:
        return retrieve_any_from_df_dict(Pt_sources, CASRN, 'Pt') 
triple_point_pressure = Pt
