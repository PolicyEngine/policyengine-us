from policyengine_us.model_api import *


def snap_monthly_fpg_amounts(spm_unit, period, parameters):
    """Monthly poverty guideline for the first person and for each additional
    person, from the guidelines SNAP adopts each October 1 (7 CFR 273.9(a)(3)).
    """
    state_group = spm_unit.household("state_group_str", period.this_year)
    year = period.start.year
    month = period.start.month
    if month >= 10:
        instant_str = f"{year}-10-01"
    else:
        instant_str = f"{year - 1}-10-01"
    p_fpg = parameters(instant_str).gov.hhs.fpg
    first_person = p_fpg.first_person[state_group] / MONTHS_IN_YEAR
    additional_person = p_fpg.additional_person[state_group] / MONTHS_IN_YEAR
    return first_person, additional_person


def snap_monthly_income_standard(spm_unit, period, parameters, rate):
    """Monthly SNAP income standard at `rate` times the poverty guideline.

    7 CFR 273.9(a)(3) rounds the monthly standard up to the next whole dollar.
    For households larger than the threshold size, it rounds the per-person
    increment up separately and adds it to the standard for the threshold
    size, so the standard can exceed rounding up the whole product.
    """
    p = parameters(period).gov.usda.snap.income.limit
    fpg = spm_unit("snap_fpg", period)
    size = spm_unit("snap_unit_size", period)
    _, increment = snap_monthly_fpg_amounts(spm_unit, period, parameters)
    additional_people = max_(size - p.increment_household_size_threshold, 0)
    # Derive the threshold-size guideline from snap_fpg so that inputs
    # overriding snap_fpg still determine the standard.
    threshold_size_fpg = fpg - additional_people * increment
    # Round to cents before taking the ceiling so float error on an exact
    # whole-dollar amount cannot push it up an extra dollar.
    standard = np.ceil(np.round(rate * threshold_size_fpg, 2))
    rounded_increment = np.ceil(np.round(rate * increment, 2))
    return standard + additional_people * rounded_increment
