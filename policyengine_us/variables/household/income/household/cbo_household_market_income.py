from policyengine_us.model_api import *


class cbo_household_market_income(Variable):
    value_type = float
    entity = Household
    label = "CBO household market income"
    documentation = (
        "Household market income under the Congressional Budget Office "
        "distributional framework: PolicyEngine household market income, less "
        "government cash assistance and the Alaska Permanent Fund Dividend, "
        "plus employer-sponsored insurance premiums and the modeled federal "
        "employer payroll tax components. Corporate income tax incidence is "
        "not yet allocated in the default PE-US benchmark."
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
