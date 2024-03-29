from policyengine_core.data import Dataset
from policyengine_us.data.storage import STORAGE_FOLDER
import policyengine_us.variables.household
from policyengine_us.variables.household.demographic.person.race import Race
from .raw_scf import (
    RawSCF_2022,
    RawSCF
)
import h5py
import numpy as np
import pandas as pd
import os
from typing import Type, Tuple
import importlib
import inspect


class SCF(Dataset):
    name  = "scf"
    label = "SCF"
    raw_scf: Type[RawSCF] = None
    data_format = Dataset.ARRAYS

    # Mapping between SCF and PolicyEngine microsim variables
    #  key = SCF variable name
    #       -- name = microsim variable name
    #       -- map  = either a dictionary map between SCF value -> microsim value
    #                   or a function to map SCF value --> microsim value
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
                               , 'map'  : {  1 : Race.WHITE.value       
                                           , 2 : Race.BLACK.value       
                                           , 3 : Race.HISPANIC.value    
                                           , 4 : Race.OTHER.value       # 4 = not defined in SDA SCF codebook, but seems to be in SCF data
                                           , 5 : Race.OTHER.value} }    
        ,   'nown'          : {  'name' : 'household_vehicles_owned'
                               , 'map'  : (lambda x : x) }
        ,   'vehic'         : {  'name' : 'household_vehicles_value'
                               , 'map'  : (lambda x : x) }
        ,   'income'        : {  'name' : 'household_net_income'
                               , 'map'  : (lambda x : x) }
        ,   'wageinc'       : {  'name' : 'employment_income_last_year'
                               , 'map'  : (lambda x : x) }

        # The following are variables not in CPS
        ,   'asset'         : {  'name' : 'assets_total'
                               , 'map'  : (lambda x : x) }
        ,   'debt'          : {  'name' : 'debt_total'
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

        # Import the SCF household data
        raw_data = self.raw_scf(require=True).load()
        hh_data  = raw_data['household']

        # Create output file with processed variables
        scf = h5py.File(self.file_path, mode="w")
        for scf_var in self._scf_mapper.keys() :
            microsim_var, vals = _remap_variable(scf_var, hh_data[scf_var], self._scf_mapper)
            scf[microsim_var]  = vals

        # Check that microsim variable has a matching class with same name
        # 1. Load all PolicyEngine variables
        # 2. Check that SCF variables are in that collection
        var_classes = []
        p_path = policyengine_us.variables.household.__path__._path[0]
        for root, _, files in os.walk(p_path):
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    file_path = os.path.join(root, file)
                    try:
                        spec   = importlib.util.spec_from_file_location("module_from_file", file_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                    except Exception as e:
                        raise ImportError(f"Cannot load classes from {file_path}") from e
                
                    var_classes.extend( [obj for obj in inspect.getmembers(module, inspect.isclass)] )

        for microsim_var in scf.keys() :
            has_var = any(class_name == microsim_var for class_name, _ in var_classes)
            if( not has_var ) :
                raise AttributeError(f'The variable {microsim_var} is not a valid PolicyEngine variable.')
    
        raw_data.close()
        scf.close()

        # Log success
        print( f'Processed raw SCF to SCF data file {self.file_path}')


def _remap_variable( varname : str, in_vals : Type[pd.Series | np.ndarray], varmap : dict ) -> Tuple[str, np.ndarray]:
    """
    Map variables using the dict map.
    map keys are the source variable names
    map values are dicts {'name' : microsim variable, 'map' : m}
    where m is either a dict which maps (source_var value) --> microsim var value
        or a function which maps (source_var value) --> microsim var value
    """
    entry        = varmap[ varname ]
    microsim_var = entry['name']
    valmap       = entry['map']

    # Ensure varvals is numpy array
    if( isinstance(in_vals, pd.Series )) :
        vector_vals = in_vals.to_numpy()
    elif( isinstance(in_vals, np.ndarray)) :
        vector_vals = in_vals
    else :
        raise ValueError('Expected pandas Series or numpy array for input values.')
    
    # Prepare function for application to input variable array
    if( isinstance(valmap, dict) ) :
        f = lambda x: valmap[x]
    else :
        f = valmap

    vector_f = np.vectorize(f)
    out_vals = vector_f(vector_vals)

    return microsim_var, out_vals


class SCF_2022(SCF):
    name        = "scf_2022"
    label       = "SCF 2022"
    raw_scf     = RawSCF_2022
    file_path   = os.path.join( STORAGE_FOLDER, f"{name}.h5" )
    time_period = 2022


