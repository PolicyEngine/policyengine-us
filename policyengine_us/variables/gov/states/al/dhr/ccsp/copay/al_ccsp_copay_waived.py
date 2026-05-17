from policyengine_us.model_api import *


class al_ccsp_copay_waived(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alabama CCSP copay waived"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = (
        "Alabama CCDF State Plan 2025-2027, Section 3.3.1",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=43",
    )

    def formula(spm_unit, period, parameters):
        p_age = parameters(period).gov.states.al.dhr.ccsp.age
        person = spm_unit.members
        is_disabled = person("is_disabled", period.this_year)
        age = person("age", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        has_disabled_child = spm_unit.any(
            is_disabled & is_dependent & (age < p_age.disabled_child_limit)
        )
        has_head_start_child = add(spm_unit, period, ["is_enrolled_in_head_start"]) > 0
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        return has_disabled_child | has_head_start_child | has_foster_child
