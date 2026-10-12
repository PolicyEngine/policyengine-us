from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


def ok_ssp_income(person, period, parameters, combined):
    p = parameters(period).gov.states.ok.dhs.ssp
    ssi = parameters(period).gov.ssa.ssi
    # 317:35-5-42(i) rounds each monthly source before applying exclusions.
    earned = sum(
        np.floor(max_(person(source, period), 0) + 0.5)
        for source in ssi.income.sources.earned
    )
    unearned = sum(
        np.floor(max_(person(source, period), 0) + 0.5)
        for source in ssi.income.sources.unearned
        if source not in ("interest_income", "dividend_income")
    )
    child = person("is_child", period.this_year)
    unearned = max_(
        unearned
        - child
        * np.floor(max_(person("child_support_received", period), 0) + 0.5)
        * ssi.income.exclusions.child_support_share,
        0,
    )
    unearned = (
        unearned
        + person("ssi_unearned_income_deemed_from_ineligible_parent", period)
        + person("ssi_in_kind_support_and_maintenance", period)
    )
    earned = max_(
        earned
        - person("ssi_blind_or_disabled_working_student_exclusion", period)
        - person("is_blind", period.this_year) * p.blind_earned_exclusion,
        0,
    )
    benefit = person("ssi", period)
    # VTR shelter is counted separately, without the $20 income exclusion.
    arrangement = person("ssi_federal_living_arrangement", period)
    vtr = arrangement == arrangement.possible_values.ANOTHER_PERSONS_HOUSEHOLD
    joint = person("ssi_couple_computation_applies", period)
    shelter = (
        vtr
        * where(joint, ssi.amount.couple / 2, ssi.amount.individual)
        * ssi.amount.one_third_reduction_rate
    )
    if combined:
        eligible = person("ok_ssp_eligible", period)
        allocation = ~eligible * person("ok_ssp_spouse_child_allocation", period)
        earned = max_(earned - max_(allocation - unearned, 0), 0)
        unearned = max_(unearned - allocation, 0)
        included = ~person("ok_ssp_is_in_tanf_unit", period)
        earned = person.marital_unit.sum(earned * included)
        unearned = person.marital_unit.sum(unearned * included)
        benefit = person.marital_unit.sum(benefit * included)
        shelter = person.marital_unit.sum(shelter * included)
    countable = (
        _apply_ssi_exclusions(
            earned * MONTHS_IN_YEAR, unearned * MONTHS_IN_YEAR, parameters, period
        )
        / MONTHS_IN_YEAR
    )
    # SSI is needs-based income and does not consume the general exclusion.
    return countable + benefit + shelter
