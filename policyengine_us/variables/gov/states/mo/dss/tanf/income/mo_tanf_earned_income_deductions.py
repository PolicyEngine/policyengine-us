from policyengine_us.model_api import *


class mo_tanf_earned_income_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Missouri TANF earned income deductions for Percentage of Need test"
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-30/",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        # Simplified implementation: Apply standard work exemption only
        # (assuming steady state, no time-limited disregards)
        # NOTE: Full implementation would track two-thirds, $30+1/3, $30, and new spouse disregards
        standard_work_exemption = spm_unit(
            "mo_tanf_standard_work_exemption", period
        )
        child_care_deduction = spm_unit("mo_tanf_child_care_deduction", period)

        return standard_work_exemption + child_care_deduction
