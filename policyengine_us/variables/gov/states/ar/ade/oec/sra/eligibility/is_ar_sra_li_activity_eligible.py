from policyengine_us.model_api import *


class is_ar_sra_li_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Activity-eligible for Arkansas SRA Low-Income track"
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = (
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=16",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.eligibility
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours = person("weekly_hours_worked", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        meets_threshold = (hours >= p.activity_hours_li) | is_student
        # All adults (heads/spouses) must meet the threshold.
        return spm_unit.sum(is_head_or_spouse & ~meets_threshold) == 0
