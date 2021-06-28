from openfisca_core.model_api import *
from openfisca_us.entities import *

def parametric_reform(modifier_func):
    class reform(Reform):
        def apply(self):
            self.modify_parameters(modifier_func)

    return reform

def reform_from_file(filepath: str):
    def replace_parameters(parameters):
        parameters = load_parameter_file(filepath)
        return parameters
    
    return parametric_reform(replace_parameters)