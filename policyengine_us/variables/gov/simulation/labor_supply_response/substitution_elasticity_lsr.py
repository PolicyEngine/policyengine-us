from policyengine_us.model_api import *


class substitution_elasticity_lsr(Variable):
    value_type = float
    entity = Person
    label = "substitution elasticity of labor supply response"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_behavioral_response"

    def formula(person, period, parameters):
        lsr = parameters(period).gov.simulation.labor_supply_responses
        employment_income = person("employment_income_before_lsr", period)
        self_employment_income = person(
            "self_employment_income_before_lsr", period
        )
        earnings = employment_income + self_employment_income
        wage_change = person("relative_wage_change", period)
        return (
            earnings * wage_change * person("substitution_elasticity", period)
        )