from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicare.savings_programs.income._msp_spouse_income import (
    msp_countable_amounts,
    msp_spouses_combine_income,
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
        "https://www.medicaid.gov/sites/default/files/2019-12/medicaid-eligibilty-memo.pdf#page=2",
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

    For married couples where both spouses are Medicare-eligible, both spouses'
    incomes are combined before exclusions are applied, and the $20 exclusion is
    taken once on the combined income.

    A spouse who is not on Medicare and is eligible for SSI (20 CFR 416.1801(c))
    is not an ineligible spouse, so nothing is deemed from that spouse and the
    person is tested alone. Any other spouse is an ineligible spouse under 20 CFR
    416.1160(d), even one who is aged, blind or disabled. Under 20 CFR 416.1163,
    allocations for ineligible children come off that spouse's income. A remainder
    above the difference between the couple and individual benefit rates is added
    to the person's own income before exclusions, and otherwise nothing is deemed.
    A medical treatment facility that separates a couple leaves each with their
    own income (20 CFR 416.414(b)(3)). Deeming cannot leave a person better off
    than their own income would (20 CFR 416.1163(e)(2)), so a person whose own
    income is the stricter test against the one-person FPL keeps their own income.
    The eligibility variables (is_qmb_eligible, is_slmb_eligible, is_qi_eligible)
    compare the result with msp_fpg, which is the couple FPL whenever
    msp_tests_as_couple is true.

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
        spouse = _ssi_spouse_index(person, period.this_year)
        personal_countable_income, deemed_countable, couple_countable = (
            msp_countable_amounts(person, period, parameters, spouse)
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
