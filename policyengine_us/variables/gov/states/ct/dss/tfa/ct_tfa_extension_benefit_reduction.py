"""
Connecticut TFA extension period benefit reduction for high earners.
"""

from policyengine_us.model_api import *


class ct_tfa_extension_benefit_reduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA extension period benefit reduction"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Connecticut reduces TFA benefits by 20% for families with earnings "
        "between 171% and 230% of Federal Poverty Level during the extension "
        "period (effective January 1, 2024)."
    )
    reference = (
        "Connecticut TANF State Plan 2024-2026, Extension Period Section; "
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ct.dss.tfa.extension_benefit_reduction
        federal = parameters(period).gov.hhs

        gross_earned = spm_unit("ct_tfa_gross_earned_income", period)
        size = spm_unit("ct_tfa_assistance_unit_size", period.this_year)

        # Calculate Federal Poverty Level for household size
        fpg_base = federal.fpg.first_person
        fpg_increment = federal.fpg.additional_person
        annual_fpl = fpg_base + fpg_increment * max_(size - 1, 0)
        monthly_fpl = annual_fpl / 12

        # Check if earnings are in the reduction range (171% - 230% FPL)
        lower_threshold = monthly_fpl * p.reduction_threshold_lower
        upper_threshold = monthly_fpl * p.reduction_threshold_upper

        in_reduction_range = (gross_earned >= lower_threshold) & (
            gross_earned <= upper_threshold
        )

        # Calculate base benefit before reduction
        payment_standard = spm_unit("ct_tfa_payment_standard", period)
        countable_income = spm_unit("ct_tfa_countable_income", period)
        base_benefit = max_(payment_standard - countable_income, 0)

        # Apply 20% reduction if in range
        reduction_rate = p.reduction_rate
        reduction = where(in_reduction_range, base_benefit * reduction_rate, 0)

        return reduction
