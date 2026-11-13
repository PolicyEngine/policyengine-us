"""Spousal-deeming comparisons for annual program budgets."""

from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)


def ssi_annual_spousal_deeming_applies(person, period, parameters):
    """Compare annual residual spouse income with the annual FBR difference."""
    spouse_income = add(
        person,
        period,
        [
            "ssi_earned_income_deemed_from_ineligible_spouse",
            "ssi_unearned_income_deemed_from_ineligible_spouse",
        ],
    )
    p = parameters(period).gov.ssa.ssi.amount
    return person("is_ssi_aged_blind_disabled", period) & (
        spouse_income > (p.couple - p.individual) * MONTHS_IN_YEAR
    )


def ssi_budget_spousal_deeming_applies(person, period, parameters):
    """Follow a program budget's period and preserve supplied annual flags."""
    if period.unit == MONTH:
        return person("is_ssi_spousal_deeming_applies_monthly", period)
    supplied = annual_input(person, period, "is_ssi_spousal_deeming_applies")
    if supplied is not None:
        return supplied
    return ssi_annual_spousal_deeming_applies(person, period, parameters)
