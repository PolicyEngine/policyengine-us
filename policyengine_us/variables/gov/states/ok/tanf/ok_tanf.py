from policyengine_us.model_api import *


class ok_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oklahoma TANF"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK

    """    
    def formula(spm_unit, period, parameters):
    """
