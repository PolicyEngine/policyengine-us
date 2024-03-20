from policyengine_core.data import Dataset
from policyengine_us.data.storage import STORAGE_FOLDER
from raw_scf import (
    RawSCF_2022,
    RawSCF
)
import h5py
import numpy as np
import pandas as pd
import os
from typing import Type, Any, Tuple


class SCF(Dataset):
    name = "scf"
    label = "SCF"
    raw_scf: Type[RawSCF] = None
    data_format = Dataset.ARRAYS


    # Mapping between SCF and microsim vars
    #  key = SCF var name
    #       -- name = microsim var name
    #       -- map  = either a dictionary map between SCF value -> microsim value
    #                   or a function to map SCF var value --> microsim value
    _scf_mapper = {
            'age'           : {  'name' : 'age'
                               , 'map'  : (lambda x : x) }
        ,   'hhsex'         : {  'name' : 'gender'
                               , 'map'  : {1 : 0, 2 : 1}}
        ,   'married'       : {  'name' : 'marital_status'
                               , 'map'  : {1 : 0, 2 : 1}}
        }

    def generate(self):
        """Generates the Survey of Consumer Finances dataset for PolicyEngine US microsimulations.
        """

        raw_data = self.raw_scf(require=True).load()
        scf      = h5py.File(self.file_path, mode="w")

        hh_data  = raw_data['household']
        for scf_var in self._scf_mapper.keys() :
            microsim_var, vals = _remap_variable(scf_var, hh_data[scf_var], self._scf_mapper)
            scf[microsim_var] = vals

        raw_data.close()
        scf.close()

        # Log success
        print( f'Converted raw SCF in file {self.file_path}')


def _remap_variable( varname : str, varvals : Type[pd.Series | np.ndarray], map : dict ) -> Tuple[str, np.ndarray]:
    """
    Map variables using the dict map.
    map keys are the source variable names
    map values are dicts {'name' : microsim variable, 'map' : m}
    where m is either a dict which maps (source_var value) --> microsim var value
        or a function which maps (source_var value) --> microsim var value
    """
    m = map[ varname ]
    
    microsim_var = m['name']
    valmap       = m['map']
    if( isinstance(varvals, pd.Series )) :
        vector_vals = varvals.to_numpy()
    elif( isinstance(varvals, np.ndarray)) :
        vector_vals = varvals
    else :
        raise ValueError('Expected pandas Series or numpy array for <varvals>.')
    
    if( isinstance(valmap, dict) ) :
        f = lambda x: valmap[x]
    else :
        # defined function
        f = lambda x: valmap(x)

    vector_f = np.vectorize(f)
    return microsim_var, vector_f(vector_vals)
    

class SCF_2022(SCF):
    name        = "scf_2022"
    label       = "SCF 2022"
    raw_scf     = RawSCF_2022
    file_path   = os.path.join( STORAGE_FOLDER, "scf_2022.h5" )
    time_period = 2022


