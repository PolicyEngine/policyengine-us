from policyengine_us.model_api import *


class child_care_provider(Variable):
    value_type = int
    entity = SPMUnit
    label = "California CalWORKs Child Care Provider"
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        