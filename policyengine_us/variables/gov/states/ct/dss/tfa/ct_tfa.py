"""
Connecticut Temporary Family Assistance (TFA) benefit amount.
"""

from policyengine_us.model_api import *


class ct_tfa(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut TFA benefit"
    definition_period = MONTH
    defined_for = StateCode.CT
    unit = USD
    documentation = (
        "Monthly cash assistance benefit amount from Connecticut's Temporary Family "
        "Assistance (TFA) program, Connecticut's implementation of federal TANF. "
        "Benefit equals the payment standard for the household's region and size, "
        "minus countable income, minus any family cap reduction, minus any extension "
        "period high earner reduction."
    )
    reference = (
        "Connecticut General Statutes Section 17b-112; "
        "Connecticut TANF State Plan 2024-2026; "
        "https://www.cga.ct.gov/current/pub/chap_319s.htm; "
        "https://portal.ct.gov/-/media/departments-and-agencies/dss/economic-security/ct-tanf-state-plan-2024---2026---41524-amendment.pdf"
    )

    def formula(spm_unit, period, parameters):
        eligible = spm_unit("ct_tfa_eligible", period)

        # Payment standard based on region and household size
        payment_standard = spm_unit("ct_tfa_payment_standard", period)

        # Countable income (after disregards)
        countable_income = spm_unit("ct_tfa_countable_income", period)

        # Calculate base benefit (payment standard minus countable income)
        base_benefit = max_(payment_standard - countable_income, 0)

        # Apply family cap reduction if applicable
        family_cap_reduction = spm_unit("ct_tfa_family_cap_reduction", period)

        # Apply extension period benefit reduction if applicable
        extension_reduction = spm_unit(
            "ct_tfa_extension_benefit_reduction", period
        )

        # Final benefit calculation
        final_benefit = max_(
            base_benefit - family_cap_reduction - extension_reduction, 0
        )

        return where(eligible, final_benefit, 0)
