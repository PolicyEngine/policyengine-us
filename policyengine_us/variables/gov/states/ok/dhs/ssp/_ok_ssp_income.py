from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


def ok_ssp_income(person, period, parameters, *, combined):
    p = parameters(period).gov.states.ok.dhs.ssp
    ssi = parameters(period).gov.ssa.ssi
    # 317:35-5-42(i) rounds each monthly source before applying exclusions.
    earned = 0
    for source in ssi.income.sources.earned:
        amount = max_(person(source, period), 0)
        if source == "employment_income":
            # As in ssi_earned_income, salary-reduction health premiums are
            # not wages (POMS SI 00820.102).
            premiums = max_(person("pre_tax_health_insurance_premiums", period), 0)
            amount = amount - min_(amount, premiums)
        earned = earned + np.floor(amount + 0.5)
    unearned = 0
    for source in ssi.income.sources.unearned:
        if source not in p.excluded_unearned_sources:
            unearned = unearned + np.floor(max_(person(source, period), 0) + 0.5)
    # 317:35-5-42(f)(11) excludes one-third of a child's child support.
    # Federal SSI does not apply 20 CFR 416.1124(c)(11) yet (issue 10242).
    child = person("is_child", period.this_year)
    unearned = max_(
        unearned
        - child
        * np.floor(max_(person("child_support_received", period), 0) + 0.5)
        * ssi.income.exclusions.child_support_share,
        0,
    )
    # NOTE: the deemed parental income uses the federal ineligible-child
    # allocation (couple FBR minus individual FBR, 497 in 2026); Appendix C-1
    # Schedule VIII.C lists 498, so a sibling's allocation can be $1 lower.
    unearned = unearned + person(
        "ssi_unearned_income_deemed_from_ineligible_parent", period
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
    # ssi_pmv_amount gives each member of an SSI couple the whole couple
    # presumed maximum value, which federal SSI counts once per couple.
    # NOTE: federal SSI also runs a couple computation for an aged, blind or
    # disabled spouse who is not eligible (issue 10243), so the half equals the
    # deeming value (1/6 couple FBR + $10) even when 317:35-5-42(m)(4) deems
    # nothing and the individual value would apply.
    ism = person("ssi_in_kind_support_and_maintenance", period)
    ism = where(joint, ism / 2, ism)
    if combined:
        eligible = person("ok_ssp_eligible", period)
        # 317:35-5-42(l)(12) excludes an ineligible spouse's in-kind support
        # and maintenance.
        unearned = unearned + ism * eligible
        allocation = ~eligible * person("ok_ssp_spouse_child_allocation", period)
        earned = max_(earned - max_(allocation - unearned, 0), 0)
        unearned = max_(unearned - allocation, 0)
        earned = person.marital_unit.sum(earned)
        unearned = person.marital_unit.sum(unearned)
        # 317:35-5-42(l)(2) excludes an ineligible spouse's SSI.
        benefit = person.marital_unit.sum(benefit * eligible)
        # 317:35-5-42(b)(8)(A) counts the one-third value once, for the
        # individual or the eligible couple, never for an ineligible spouse.
        shelter = person.marital_unit.sum(shelter * eligible)
    else:
        unearned = unearned + ism
    countable = (
        _apply_ssi_exclusions(
            earned * MONTHS_IN_YEAR, unearned * MONTHS_IN_YEAR, parameters, period
        )
        / MONTHS_IN_YEAR
    )
    # SSI is needs-based income and does not consume the general exclusion.
    return countable + benefit + shelter
