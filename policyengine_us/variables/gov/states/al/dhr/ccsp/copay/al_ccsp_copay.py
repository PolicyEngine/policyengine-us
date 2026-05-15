from policyengine_us.model_api import *


class al_ccsp_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama CCSP monthly family copay"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = (
        "Alabama CCDF State Plan 2025-2027, Section 3.3.1",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=43",
    )

    def formula(spm_unit, period, parameters):
        p_elig = parameters(period).gov.states.al.dhr.ccsp.eligibility
        weekly_per_child = spm_unit("al_ccsp_weekly_copay_per_child", period)

        # Copay waivers (§3.3.1):
        #   (iv) family includes a disabled child
        #   (v)  family enrolled in Head Start / EHS
        #   (vi) foster care (protective-services category for copay)
        # Homelessness alone does NOT waive copay (§3.3.1(iii) unchecked),
        # though it triggers the eligibility waiver via protective_services.
        person = spm_unit.members
        is_disabled = person("is_disabled", period.this_year)
        age = person("age", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        has_disabled_child = spm_unit.any(
            is_disabled & is_dependent & (age < p_elig.disabled_child_age_limit)
        )

        is_head_start = person("is_enrolled_in_head_start", period.this_year)
        has_head_start_child = spm_unit.any(is_head_start)

        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0

        copay_waived = has_disabled_child | has_head_start_child | has_foster_child

        # Count children whose copay applies: eligible children in care.
        is_eligible_child = person("al_ccsp_eligible_child", period)
        in_care = person("childcare_hours_per_week", period.this_year) > 0
        num_paying = spm_unit.sum(is_eligible_child & in_care)

        # Provider may charge above max reimbursement rate (§3.1); copay
        # is independent of the rate and based on the FPL fee table.
        weekly_family_copay = weekly_per_child * num_paying
        weeks_to_months = parameters(
            period
        ).gov.states.al.dhr.ccsp.income.weeks_to_months
        monthly_family_copay = weekly_family_copay * weeks_to_months
        return where(copay_waived, 0, monthly_family_copay)
