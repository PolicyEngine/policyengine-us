from policyengine_us.model_api import *


class ma_eaedc_eligible_caretaker_family(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible caretaker family for the Massachusetts EAEDC"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-703-700"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tcap.eaedc.age_threshold
        person = spm_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        meets_age_limit = age < p.dependent
        is_related_to_head_or_spouse = person(
            "is_tafdc_related_to_head_or_spouse", period
        )
        eligible_dependent_present = spm_unit.any(
            is_dependent & meets_age_limit & ~is_related_to_head_or_spouse
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age_eligible_caretaker = age >= p.caretaker
        eligible_caretaker_present = spm_unit.any(
            age_eligible_caretaker & head_or_spouse
        )
        return eligible_dependent_present & eligible_caretaker_present
