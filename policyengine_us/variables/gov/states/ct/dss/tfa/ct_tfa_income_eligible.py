"""
Connecticut TFA income eligibility.
"""

from policyengine_us.model_api import *


class ct_tfa_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Connecticut TFA income eligibility"
    definition_period = MONTH
    defined_for = StateCode.CT
    documentation = (
        "Connecticut TFA income eligibility varies by status. New applicants must "
        "have earned income under 55% of FPL (the Standard of Need). Once enrolled, "
        "households can earn up to 100% of FPL with full earned income disregard. "
        "During the extension period (effective January 1, 2024), families may "
        "continue receiving benefits for up to 6 months with earnings disregarded "
        "up to 230% of FPL for eligibility purposes."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026, Income Eligibility Section; "
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa
        federal = parameters(period).gov.hhs

        gross_earned = spm_unit("ct_tfa_gross_earned_income", period)
        gross_unearned = spm_unit("ct_tfa_gross_unearned_income", period)
        size = spm_unit("ct_tfa_assistance_unit_size", period.this_year)

        # Calculate Federal Poverty Level for household size
        fpg_base = federal.fpg.first_person
        fpg_increment = federal.fpg.additional_person
        annual_fpl = fpg_base + fpg_increment * max_(size - 1, 0)
        monthly_fpl = annual_fpl / 12

        # Use extension limit as the maximum income eligibility threshold
        # This covers initial (55% FPL), continuing (100% FPL), and extension (230% FPL)
        extension_limit = monthly_fpl * p.income_limits.extension

        # Income eligible if gross earned income is below extension limit
        # and unearned income is below standard of need (55% FPL)
        initial_limit = monthly_fpl * p.income_limits.initial
        income_eligible = (gross_earned < extension_limit) & (
            gross_unearned < initial_limit
        )

        return income_eligible
