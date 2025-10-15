"""
Connecticut TFA countable earned income after disregards.
"""

from policyengine_us.model_api import *


class ct_tfa_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA countable earned income"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Connecticut TFA earned income after applying applicable disregards. "
        "At initial application, $90 is deducted from each person's gross earnings. "
        "Once enrolled, earned income is fully disregarded up to 100% of FPL. "
        "During the extension period (effective January 1, 2024), earnings are "
        "disregarded up to 230% of FPL for eligibility purposes."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026, Income Disregard Section; "
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.tfa
        federal = parameters(period).gov.hhs

        gross_earned = spm_unit("ct_tfa_gross_earned_income", period)
        size = spm_unit("ct_tfa_assistance_unit_size", period.this_year)

        # Calculate Federal Poverty Level for household size
        fpg_base = federal.fpg.first_person
        fpg_increment = federal.fpg.additional_person
        annual_fpl = fpg_base + fpg_increment * max_(size - 1, 0)
        monthly_fpl = annual_fpl / 12

        # For continuing eligibility calculation, we apply full earned income disregard
        # up to 100% FPL. The benefit calculation will subtract this from payment standard.
        # During extension period, earnings up to 230% FPL are disregarded for eligibility,
        # but may still affect benefit amount.

        # Apply continuing disregard: 100% up to FPL
        continuing_limit = monthly_fpl * p.income_limits.continuing
        disregard = min_(gross_earned, continuing_limit)

        # Countable earned income is gross minus disregard
        countable = max_(gross_earned - disregard, 0)

        return countable
