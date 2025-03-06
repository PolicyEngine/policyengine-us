from policyengine_us.model_api import *


class ma_eaedc_disabled_dependent_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Massachusetts EAEDC based on disabled dependent status"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-620"  

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_disabled = person("is_disabled", period)
        is_dependent = person("is_tax_unit_dependent", period)
        return spm_unit.any(is_disabled & is_dependent)
