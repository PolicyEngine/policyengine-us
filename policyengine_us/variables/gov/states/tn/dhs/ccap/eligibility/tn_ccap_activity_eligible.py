from policyengine_us.model_api import *


class tn_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Tennessee CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.TN
    reference = "https://www.tn.gov/content/dam/tn/human-services/documents/CCDF%20State%20Plan%20FFY%202025-2027%20Tennessee.pdf#page=26"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap.activity
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        employment_income = person("employment_income", period.this_year)
        self_employment_income = person("self_employment_income", period.this_year)
        sstb_self_employment_income = person(
            "sstb_self_employment_income", period.this_year
        )
        has_employment = (
            (employment_income > 0)
            | (self_employment_income != 0)
            | (sstb_self_employment_income != 0)
        )
        meets_work_requirement = has_employment & (hours_worked >= p.weekly_hours)
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = meets_work_requirement | is_student
        n_parents = spm_unit.sum(is_head_or_spouse)
        n_qualifying = spm_unit.sum(is_head_or_spouse & individually_eligible)
        all_parents_qualify = (n_parents >= 1) & (n_qualifying >= n_parents)

        # NOTE: Inability to meet the child's care needs is not modeled separately.
        is_disabled = person("is_disabled", period.this_year)
        n_exempt_parents = spm_unit.sum(is_head_or_spouse & is_disabled)
        n_working_non_disabled_parents = spm_unit.sum(
            is_head_or_spouse & ~is_disabled & meets_work_requirement
        )
        disabled_parent_exception = (
            (n_parents == 2)
            & (n_exempt_parents == 1)
            & (n_working_non_disabled_parents == 1)
        )

        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return all_parents_qualify | disabled_parent_exception | fallback
