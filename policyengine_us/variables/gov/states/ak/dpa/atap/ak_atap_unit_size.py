from policyengine_us.model_api import *


class ak_atap_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Alaska ATAP assistance unit size"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.335"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Use SPM unit size as approximation for assistance unit size
        return spm_unit.nb_persons()
