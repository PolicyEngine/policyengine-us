from policyengine_us.model_api import *


class cbo_household_market_income(Variable):
    value_type = float
    entity = Household
    label = "CBO household market income"
    documentation = (
        "Household market income under the Congressional Budget Office "
        "distributional framework: PolicyEngine household market income, less "
        "government cash assistance and the Alaska Permanent Fund Dividend, "
        "plus employer-sponsored insurance premiums, employer payroll taxes, "
        "and allocated corporate income taxes."
    )
    definition_period = YEAR
    unit = USD

    def formula(household, period, parameters):
        p = parameters(period)
        base = household("household_market_income", period)
        additions = add(household, period, p.gov.household.cbo_market_income_additions)
        subtractions = add(
            household, period, p.gov.household.cbo_market_income_subtractions
        )
        return base + additions - subtractions
