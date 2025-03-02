from policyengine_us.model_api import *


class ma_eaedc_caretaker_family_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Massachusetts EAEDC caretaker family eligible"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-700"  # (A)

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.eaedc.deductions.dependent_care
        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        meets_age_limit = age < p.dependent_age_threshold
        return spm_unit.any(is_dependent & meets_age_limit)
