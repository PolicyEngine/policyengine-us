"""Shared calculations for state LIHEAP regular heating assistance."""

import numpy as np
from policyengine_core.model_api import MONTHS_IN_YEAR, clip, max_


def calculate_liheap_fpg_income_limit(
    household_size, state_group, period, parameters, policy
):
    """Annualize a monthly FPG limit with separately rounded size increments.

    The caller supplies its policy household size, modeled period, and dated
    parameters: fpg_year_lag, fpg_rate, rounding_increment, and max_table_size.
    Guideline amounts come from the shared federal parameters for the modeled
    year minus the guideline-year lag. Round to the nearest
    increment, with ties rounded up, before adding people beyond the breakpoint.
    """
    fpg_year = period.start.year - int(policy.fpg_year_lag)
    fpg = parameters(f"{fpg_year}-01-01").gov.hhs.fpg
    first_person = fpg.first_person[state_group]
    additional_person = fpg.additional_person[state_group]
    capped_size = clip(household_size, 1, policy.max_table_size)
    additional_people = max_(household_size - policy.max_table_size, 0)
    monthly_factor = policy.fpg_rate / MONTHS_IN_YEAR
    monthly_limit = (
        first_person + additional_person * (capped_size - 1)
    ) * monthly_factor
    monthly_increment = additional_person * monthly_factor
    rounding = policy.rounding_increment
    rounded_limit = np.floor(monthly_limit / rounding + 0.5) * rounding
    rounded_increment = np.floor(monthly_increment / rounding + 0.5) * rounding
    return (rounded_limit + additional_people * rounded_increment) * MONTHS_IN_YEAR
