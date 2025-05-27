from policyengine_us.model_api import *
from policyengine_us.variables.gov.simulation.labor_supply_response.helpers import pos


class income_elasticity_lsr(Variable):
    value_type = float
    entity = Person
    label = "income elasticity of labor supply response"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_behavioral_response"

    def formula(person, period, parameters):
        lsr = parameters(period).gov.simulation.labor_supply_responses
        employment_income = person("employment_income_before_lsr", period)
        self_employment_income = person(
            "self_employment_income_before_lsr", period
        )
        earnings = pos(employment_income + self_employment_income)
        income_change = person("relative_income_change", period)
        return earnings * income_change * person("income_elasticity", period)