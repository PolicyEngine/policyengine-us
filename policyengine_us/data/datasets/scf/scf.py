from policyengine_core.data import Dataset
from policyengine_us.data.storage import STORAGE_FOLDER
from .raw_scf import (
    RawSCF_2022,
    RawSCF
)
import h5py
import numpy as np
import pandas as pd
import os
from typing import Type, Any, Tuple

from policyengine_us.variables.household.demographic.person.race import Race

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
        ,   'hhsex'         : {  'name' : 'is_female'
                               , 'map'  : {1 : False, 2 : True} }
        ,   'kids'          : {  'name' : 'spm_unit_count_children'
                               , 'map'  : (lambda x : x) }
        ,   'married'       : {  'name' : 'is_married'
                               , 'map'  : {1 : True, 2 : False} }
        ,   'race'          : {  'name' : 'race'
                               , 'map'  : {  1 : Race.WHITE.value       # 1 = White
                                           , 2 : Race.BLACK.value       # 2 = Black
                                           , 3 : Race.HISPANIC.value    # 3 = Hispanic
                                           , 4 : Race.OTHER.value       # 4 = not defined in SDA SCF codebook, but seems to be in SCF data
                                           , 5 : Race.OTHER.value} }    # 5 = Other
                            # TBD: Race Enum would be better as int vs str
        ,   'nown'          : {  'name' : 'household_vehicles_owned'
                               , 'map'  : (lambda x : x) }
        ,   'vehic'         : {  'name' : 'household_vehicles_value'
                               , 'map'  : (lambda x : x) }
        ,   'income'        : {  'name' : 'household_net_income'
                               , 'map'  : (lambda x : x) }
        ,   'wageinc'       : {  'name' : 'employment_income_last_year'
                               , 'map'  : (lambda x : x) }

        ,   'asset'         : {  'name' : 'spm_unit_assets'
                               , 'map'  : (lambda x : x) }
        ,   'fin'           : {  'name' : 'assets_financial'
                               , 'map'  : (lambda x : x) }
        ,   'houses'        : {  'name' : 'assets_value_primary_residence'
                               , 'map'  : (lambda x : x) }
        ,   'cashli'        : {  'name' : 'assets_life_insurance'
                               , 'map'  : (lambda x : x) }
        ,   'othnfin'       : {  'name' : 'assets_nonfinancial_other'
                               , 'map'  : (lambda x : x) }
        ,   'homeeq'        : {  'name' : 'assets_equity_primary_residence'
                               , 'map'  : (lambda x : x) }

        }

    def generate(self):
        """
        Generates the Survey of Consumer Finances dataset for PolicyEngine US microsimulations.
        """

        raw_data = self.raw_scf(require=True).load()
        scf      = h5py.File(self.file_path, mode="w")

        hh_data  = raw_data['household']
        for scf_var in self._scf_mapper.keys() :
            microsim_var, vals = _remap_variable(scf_var, hh_data[scf_var], self._scf_mapper)
            if( vals.dtype == '<U19' ) :
                _vals    = scf.create_dataset(microsim_var, shape=(len(vals),), dtype=h5py.string_dtype(length=32))
                _vals[:] = vals.tolist()
            else :
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


