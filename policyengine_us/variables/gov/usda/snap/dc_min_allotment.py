from policyengine_us.model_api import *

 
class dc_min_allotment(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "DC SNAP minimum allotment"
    label = "Minimum allotment for SNAP in DC"
    unit = USD
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        # Parameters for the minimum benefit.
        dc_min_allotment = parameters(period).gov.usda.snap.min_allotment.dc_amount
        
        return dc_min_allotment