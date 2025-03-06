from policyengine_us.model_api import *


class ma_eaedc_caretaker_family_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Massachusetts EAEDC caretaker family eligible"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-700"  # (A)

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible_person = person("ma_eaedc_dependent_care_deduction_person_eligible",period)
        return spm_unit.sum(eligible_person) > 0
    