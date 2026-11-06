from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicare.savings_programs.income._msp_spouse_income import (
    msp_spouse_income,
    msp_spouse_value,
    msp_spouses_combine_income,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


class msp_countable_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program countable monthly income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396d#p",
        "https://www.law.cornell.edu/cfr/text/20/416.412",
        "https://www.law.cornell.edu/cfr/text/20/416.414",
        "https://www.law.cornell.edu/cfr/text/20/416.1160",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
        "https://www.law.cornell.edu/cfr/text/20/416.1801",
        "https://secure.ssa.gov/poms.nsf/lnx/0500501154",
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

    For married couples where both spouses are Medicare-eligible, or who are an
    eligible couple because each is eligible for SSI (20 CFR 416.412 and
    416.1801(c)), both spouses' incomes are combined before exclusions are
    applied, and the $20 exclusion is taken once on the combined income.

    Any other spouse is an ineligible spouse under 20 CFR 416.1160(d), even one
    who is aged, blind or disabled. Under 20 CFR 416.1163, allocations for
    ineligible children come off that spouse's income. A remainder above the
    difference between the couple and individual benefit rates is added to the
    person's own income before exclusions, and otherwise nothing is deemed. A
    medical treatment facility that separates a couple leaves each with their own
    income (20 CFR 416.414(b)(3)). The eligibility variables (is_qmb_eligible,
    is_slmb_eligible, is_qi_eligible) compare the result with msp_fpg, which is the
    couple FPL whenever msp_tests_as_couple is true.

    Under 42 U.S.C. 1396a(r)(2) a state may exclude more than the $20 SSI
    general income exclusion; Illinois and Mississippi use their larger
    exclusion in its place. Mississippi takes it once from a couple's
    combined income; Illinois gives each applying spouse with income their
    own exclusion, up to that spouse's income, and one exclusion when only one
    spouse is on Medicare. Illinois gives its $25 only on income other than SSI
    and contributions (alimony, child support, outside cash help); the $20 SSI
    exclusion stays the floor.
    """

    def formula(person, period, parameters):
        year = period.this_year
        earned_income = person("ssi_earned_income", year)
        unearned_income = person("ssi_unearned_income", year)
        spouse = _ssi_spouse_index(person, year)
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
            person, year, spouse
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

        single_countable = where(
            person("msp_tests_as_couple", period),
            deemed_countable,
            personal_countable_income,
        )

        annual_countable = where(
            msp_spouses_combine_income(person, period, spouse),
            couple_countable,
            single_countable,
        )
        return annual_countable / MONTHS_IN_YEAR
