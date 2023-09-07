from policyengine_us.model_api import *


class pa_tanf_age_eligible_on_pregnant_women_limitation(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF age eligibility on pregnant women requirement"
    definition_period = YEAR
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(period).gov.states.pa.dhs.tanf.pregnancy_eligibility
        age = person("age", period)
        is_eligible_age = age < p.age_limit
        is_pregnant = person("is_pregnant", period)
        is_children_receiving_tanf = spm_unit("pa_tanf_age_eligible", period)
        # Must be pregnant and either of a qualifying age or children not receiving TANF.
        eligible = is_pregnant & (
            is_eligible_age | ~is_children_receiving_tanf
        )
        return spm_unit.any(eligible)
