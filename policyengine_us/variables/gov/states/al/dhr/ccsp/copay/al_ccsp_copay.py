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

    def formula(spm_unit, period):
        weekly_per_child = spm_unit("al_ccsp_weekly_copay_per_child", period)
        person = spm_unit.members
        is_eligible_child = person("al_ccsp_eligible_child", period)
        in_care = person("childcare_hours_per_week", period.this_year) > 0
        num_paying = spm_unit.sum(is_eligible_child & in_care)

        weekly_family_copay = weekly_per_child * num_paying
        monthly_family_copay = weekly_family_copay * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        copay_waived = spm_unit("al_ccsp_copay_waived", period)
        return where(copay_waived, 0, monthly_family_copay)
