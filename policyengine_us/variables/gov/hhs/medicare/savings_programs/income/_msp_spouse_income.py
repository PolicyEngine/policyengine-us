from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


def msp_spouse_value(values: ArrayLike, spouse: ArrayLike) -> ArrayLike:
    # Each person's spouse's value, or zero for a person with no spouse. The
    # spouse is the row from _ssi_spouse_index, not the rest of the marital unit,
    # because a situation that omits marital units puts everyone in one.
    return values[np.maximum(spouse, 0)] * (spouse >= 0)


def msp_spouses_combine_income(
    person: Population, period: Period, spouse: ArrayLike
) -> ArrayLike:
    # Spouses who are both on Medicare are tested together, against the
    # two-person guideline. CMS's family-size memorandum of October 2, 1997
    # treats people in the SSI-related poverty-level groups "as individuals or,
    # if both members of a couple were eligible, as a couple", so a couple with
    # one spouse on Medicare is not tested together, even an eligible SSI couple.
    is_medicare_eligible = person("is_medicare_eligible", period.this_year)
    return is_medicare_eligible & msp_spouse_value(is_medicare_eligible, spouse)


def msp_spouse_income(person: Population, period: Period, spouse: ArrayLike) -> tuple:
    # An ineligible spouse's annual earned and unearned income after allocations
    # for ineligible children, which come off unearned income first (20 CFR
    # 416.1163(a) and (b)). Any spouse who is not eligible for SSI is an
    # ineligible spouse, whether or not aged, blind or disabled (20 CFR
    # 416.1160(d)). A spouse who is eligible for SSI is not one, so nothing is
    # deemed from that spouse. Each spouse must be eligible for SSI (20 CFR
    # 416.1801(c); POMS SI 00501.154 A.1), not only aged, blind or disabled:
    # uncapped_ssi above zero adds the income test that is_ssi_eligible leaves
    # out.
    # NOTE: SSI attributes a couple's income by the year's last month
    # (ssi_marital_unearned_income). In the months before a facility stay that
    # lasts through December, uncapped_ssi can be above zero for spouses whose
    # combined income rules SSI out, and nothing is then deemed between them.
    year = period.this_year
    spouse_eligible_for_ssi = msp_spouse_value(
        person("uncapped_ssi", period) > 0, spouse
    )
    spouse_earned = where(
        spouse_eligible_for_ssi,
        0,
        msp_spouse_value(person("ssi_earned_income", year), spouse),
    )
    spouse_unearned = where(
        spouse_eligible_for_ssi,
        0,
        msp_spouse_value(person("ssi_unearned_income", year), spouse),
    )
    allocations = add(person.tax_unit, year, ["ssi_ineligible_child_allocation"])
    earned_left = max_(spouse_earned - max_(allocations - spouse_unearned, 0), 0)
    unearned_left = max_(spouse_unearned - allocations, 0)
    return earned_left, unearned_left


def msp_countable_amounts(
    person: Population, period: Period, parameters, spouse: ArrayLike
) -> tuple:
    # A person's annual countable income three ways: from their own income alone,
    # with an ineligible spouse's income deemed, and combined with the spouse's as
    # a couple. msp_countable_income picks one; msp_tests_as_couple compares the
    # first two (20 CFR 416.1163(e)(2)).
    year = period.this_year
    earned_income = person("ssi_earned_income", year)
    unearned_income = person("ssi_unearned_income", year)
    is_medicare_eligible = person("is_medicare_eligible", year)
    both_medicare_eligible = is_medicare_eligible & msp_spouse_value(
        is_medicare_eligible, spouse
    )

    blind_or_disabled_working_student_exclusion = person(
        "ssi_blind_or_disabled_working_student_exclusion", year
    )
    personal_earned_income = max_(
        earned_income - blind_or_disabled_working_student_exclusion,
        0,
    )
    state = person.household("state_code_str", period)
    p = parameters(period).gov.hhs.medicare.savings_programs.eligibility.income
    ssi_general = parameters(period).gov.ssa.ssi.income.exclusions.general
    state_exclusion = p.state_general_exclusion[state]
    general_exclusion = max_(ssi_general, state_exclusion)
    # Illinois exempts the first $25 of income other than SSI and
    # contributions such as alimony and child support, and gives each
    # applying spouse their own exemption (PM 15-04-03-a; 89 Ill. Adm.
    # Code 120.335(a)(1)); SSI and Mississippi allow one per couple.
    # Floor each kind of income: a self-employment loss earns no exemption
    # and does not offset unearned income.
    own_monthly_income = max_(person("ssi_earned_income", period), 0) + max_(
        person("ssi_unearned_income", period), 0
    )
    excludes_contributions = p.state_general_exclusion_excludes_contributions[
        state
    ].astype(bool)
    contributions = add(person, period, p.contribution_sources)
    qualifying_income = where(
        excludes_contributions,
        max_(own_monthly_income - contributions, 0),
        own_monthly_income,
    )
    # The SSI general exclusion stays the floor (42 U.S.C. 1396a(r)(2)).
    own_general_exclusion = where(
        excludes_contributions,
        max_(ssi_general, min_(state_exclusion, qualifying_income)),
        general_exclusion,
    )
    # Two spouses on Medicare each apply. When only one does, PM 15-04-03-a
    # allows one $25 on income in the standard, even if that spouse has no
    # income other than SSI or contributions.
    per_spouse = p.state_general_exclusion_per_spouse[state].astype(bool)
    own_exemption = min_(state_exclusion, qualifying_income)
    couple_general_exclusion = where(
        per_spouse & both_medicare_eligible,
        max_(
            ssi_general,
            own_exemption + msp_spouse_value(own_exemption, spouse),
        ),
        general_exclusion,
    )

    spouse_earned_income, spouse_unearned_income = msp_spouse_income(
        person, period, spouse
    )
    personal_countable_income = _apply_ssi_exclusions(
        personal_earned_income,
        unearned_income,
        parameters,
        year,
        general_exclusion=own_general_exclusion,
    )

    couple_countable = _apply_ssi_exclusions(
        max_(
            earned_income
            + msp_spouse_value(earned_income, spouse)
            - blind_or_disabled_working_student_exclusion
            - msp_spouse_value(blind_or_disabled_working_student_exclusion, spouse),
            0,
        ),
        unearned_income + msp_spouse_value(unearned_income, spouse),
        parameters,
        year,
        general_exclusion=couple_general_exclusion,
    )

    deemed_countable = _apply_ssi_exclusions(
        personal_earned_income + spouse_earned_income,
        unearned_income + spouse_unearned_income,
        parameters,
        year,
        general_exclusion=general_exclusion,
    )
    return personal_countable_income, deemed_countable, couple_countable
