"""Retain the California WDP screens' existing annual income approximation."""

from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
    annual_input,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_spouse._ssi_annual_spousal_deeming import (
    ssi_annual_spousal_deeming_applies,
)


def ca_wdp_annual_spousal_deeming_applies(person, period, parameters):
    """Apply the SSI differential to the screens' annual income budget.

    A supplied annual flag takes precedence, as when the screens read
    is_ssi_spousal_deeming_applies directly.
    """
    supplied = annual_input(person, period, "is_ssi_spousal_deeming_applies")
    if supplied is not None:
        return supplied
    return person("is_ssi_eligible_individual", period) & (
        ssi_annual_spousal_deeming_applies(person, period, parameters)
    )
