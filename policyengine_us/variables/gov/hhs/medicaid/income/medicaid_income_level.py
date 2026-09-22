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

    This approximates state tables that additionally round the monthly FPG base.
    Inclusive standards: 42 CFR 435.110(b), 435.116(b), 435.118(b),
    435.119(b)(5), 435.222(b), and 457.310(b)(1).
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
