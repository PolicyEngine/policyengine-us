from policyengine_us.model_api import *


class az_liheap_categorical_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Arizona LIHEAP categorically eligible"
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = "https://des.az.gov/services/basic-needs/liheap"

    def formula(spm_unit, period, parameters):
        # Categorical eligibility for SNAP or TANF recipients
        receives_snap = add(spm_unit, period, ["snap"]) > 0
        receives_tanf = add(spm_unit, period, ["tanf"]) > 0

        return receives_snap | receives_tanf
