from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class msp_countable_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program countable monthly income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396d#p",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501715010",
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.law.cornell.edu/uscode/text/42/1396a#r_2",
        "https://www.dhs.state.il.us/page.aspx?item=16387",
        "https://www.ilga.gov/ftp/JCAR/AdminCode/089/089001200H03350R.html",
    )
    documentation = """
    MSP countable income uses SSI methodology per 42 U.S.C. 1396d(p)(1)(B),
    which specifies income "determined under section 1382a" (SSI rules).
    This applies the standard SSI exclusions:
    1. $20 general income exclusion (from unearned first)
    2. $65 earned income exclusion
    3. 50% of remaining earned income excluded

    For married couples where both spouses are Medicare-eligible, SSI couple
    rules apply per 20 CFR 416.1160: both spouses' incomes are combined before
    exclusions are applied, and the $20 exclusion is taken once on the combined
    income. The combined countable income is then compared against the couple FPL
    in the eligibility variables (is_qmb_eligible, is_slmb_eligible, is_qi_eligible).

    Under 42 U.S.C. 1396a(r)(2) a state may exclude more than the $20 SSI
    general income exclusion; Illinois and Mississippi use their larger
    exclusion in its place. Mississippi takes it once from a couple's
    combined income; Illinois gives each applying spouse with income their
    own exclusion, up to that spouse's income. Illinois gives its $25 only on
    income other than SSI and contributions (alimony, child support, outside
    cash help); the $20 SSI exclusion stays the floor.
    """

    def formula(person, period, parameters):
        year = period.this_year
        earned_income = person("ssi_earned_income_after_spousal_loss", year)
        unearned_income = person("ssi_unearned_income", year)
        is_medicare_eligible = person("is_medicare_eligible", year)
        both_medicare_eligible = person.marital_unit.sum(is_medicare_eligible) == 2

        blind_or_disabled_working_student_exclusion = person(
            "ssi_blind_or_disabled_working_student_exclusion", year
        )
        personal_earned_income = max_(
            earned_income - blind_or_disabled_working_student_exclusion,
            0,
        )
        deeming_applies = person("is_ssi_spousal_deeming_applies", year)
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
        per_spouse = p.state_general_exclusion_per_spouse[state].astype(bool)
        couple_general_exclusion = where(
            per_spouse,
            max_(
                ssi_general,
                person.marital_unit.sum(min_(state_exclusion, qualifying_income)),
            ),
            general_exclusion,
        )

        spouse_earned_income = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", year
        )
        spouse_unearned_income = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", year
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
                person.marital_unit.sum(earned_income)
                - person.marital_unit.sum(blind_or_disabled_working_student_exclusion),
                0,
            ),
            person.marital_unit.sum(unearned_income),
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

        single_countable = where(
            deeming_applies, deemed_countable, personal_countable_income
        )

        annual_countable = where(
            both_medicare_eligible, couple_countable, single_countable
        )
        return annual_countable / MONTHS_IN_YEAR
