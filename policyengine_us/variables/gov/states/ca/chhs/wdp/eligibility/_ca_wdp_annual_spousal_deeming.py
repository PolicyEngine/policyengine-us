"""Retain the California WDP screens' existing annual income approximation."""

from policyengine_us.model_api import *


def ca_wdp_annual_spousal_deeming_applies(person, period, parameters):
    """Apply the SSI differential to the screens' annual income budget.

    These first-pass WDP screens use annual income. The SSI deeming flag
    itself is monthly, and an annual read of that stock gives December's
    result. Compare annual aggregate spouse income with the annualized FBR
    differential here to preserve the screens' existing approximation;
    federal SSI continues to apply the threshold separately each month.
    """
    spouse_income = add(
        person,
        period,
        [
            "ssi_earned_income_deemed_from_ineligible_spouse",
            "ssi_unearned_income_deemed_from_ineligible_spouse",
        ],
    )
    p = parameters(period).gov.ssa.ssi.amount
    return person("is_ssi_eligible_individual", period) & (
        spouse_income > (p.couple - p.individual) * MONTHS_IN_YEAR
    )
