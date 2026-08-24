from policyengine_us.model_api import *


class household_head_start_benefits(Variable):
    value_type = float
    entity = Household
    label = "Household Head Start benefits"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Annual Head Start and Early Head Start value included in "
        "household_benefits only when "
        "gov.simulation.include_head_start_benefits_in_net_income is "
        "enabled. The programs are valued at per-enrollee cost and their "
        "take-up flags default to true, so datasets without seeded "
        "enrollment flags value every eligible person at full cost."
    )

    def formula(household, period, parameters):
        p = parameters(period)
        if p.gov.simulation.include_head_start_benefits_in_net_income:
            return add(household, period, p.gov.household.household_head_start_benefits)
        else:
            return 0
