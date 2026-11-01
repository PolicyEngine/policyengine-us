from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class medicaid_income_level(Variable):
    value_type = float
    entity = Person
    label = "Medicaid/CHIP-related income level"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.603",
        "https://www.medicaid.gov/state-resource-center/mac-learning-collaboratives/downloads/household-composition-and-income-training.pdf",
    )

    def formula(person, period, parameters):
        income = person("medicaid_household_income", period)
        size = person("medicaid_household_size", period)
        state_group = person.household("state_group_str", period)
        return income / fpg(size, state_group, period, parameters)


def medicaid_income_eligible(person, period, parameters, income_limit):
    """Apply one monthly whole-dollar ceiling convention in every state.

    The MAGI standards are inclusive: household income "at or below" the
    standard qualifies (42 CFR 435.110(b), 435.116(b), 435.118(b),
    435.119(b)(5), 435.222(b), and 457.310(b)(1)).

    This convention applies only to the MAGI Medicaid category and CHIP
    financial-criteria variables that call this helper. Non-MAGI pathways
    (the optional senior or disabled group and the medically needy group)
    and other direct consumers of medicaid_income_level (state programs,
    CHIP premiums, and the Basic Health Program) are unchanged and compare
    the raw ratio against their limits; a follow-up issue tracks them.

    States apply those standards through published monthly dollar tables.
    Missouri's MAGI Appendix A converts each FPL percentage to a monthly
    amount and rounds it up to the next whole dollar, and countable income
    "cannot exceed" the table amount. For example, the Adult Expansion Group
    column (133% FPL plus the 5-percentage-point MAGI disregard, a 1.38
    ratio) for a household of 5 is $4,448.20 exactly and $4,449 in the
    7/1/2026-3/31/2027 table:
    https://dssmanuals.mo.gov/wp-content/uploads/2019/03/MAGIappendix-a.pdf#page=1
    https://dssmanuals.mo.gov/family-mo-healthnet-magi/1810-000-00/1810-020-00/1810-020-10/
    https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-030-00/1805-030-20/1805-030-20-20/1805-030-20-20-05/

    This function applies that round-up convention uniformly. It is a modeling
    approximation, not an assertion that every state rounds identically:
    against a state that publishes an exact or annual standard (for example,
    California's DHCS program income eligibility comparison chart,
    https://www.dhcs.ca.gov/services/HACCP/Documents/Program-Income-Eligibility-Comparison2025.pdf#page=1)
    it admits up to $0.99 of monthly income above the exact standard, and it
    does not reproduce tables that additionally round the monthly FPG base
    before multiplying. For example, California's ACWDL 26-01 Enclosure 1
    publishes $4,799 per month for 266% FPL at a household size of 2 in
    2026, while this convention gives $4,797 (21,640 x 2.66 / 12 = 4,796.87,
    rounded up):
    https://www.dhcs.ca.gov/services/medi-cal-resources/medi-cal-eligibility-division/all-county-welfare-directors-medi-cal-eligibility-division-information-letters/2026-fpl-calculation-chart-monthly-values-enclosure-1/
    """
    income = person("medicaid_income_level", period)

    annual_fpg = fpg(
        person("medicaid_household_size", period),
        person.household("state_group_str", period),
        period,
        parameters,
    )
    # Stabilize the calculated limit at cent precision before ceiling it, so
    # floating-point noise cannot turn an exact whole dollar into an extra dollar.
    monthly_limit = np.ceil(np.round(annual_fpg * income_limit / MONTHS_IN_YEAR, 2))
    effective_limit = monthly_limit * MONTHS_IN_YEAR / annual_fpg
    # Use the same inclusive comparison for every state. Matching the stored
    # ratio's precision admits the exact limit without an isclose tolerance
    # that could also admit distinguishable income above the limit.
    return income <= np.asarray(effective_limit, dtype=income.dtype)
