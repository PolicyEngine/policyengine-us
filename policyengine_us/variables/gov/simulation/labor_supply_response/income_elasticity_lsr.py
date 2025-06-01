from policyengine_us.model_api import *


class income_elasticity_lsr(Variable):
    value_type = float
    entity = Person
    label = "income elasticity of labor supply response"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_behavioral_response"

    def formula(person, period, parameters):
        raw_earnings = add(
            person,
            period,
            [
                "employment_income_before_lsr",
                "self_employment_income_before_lsr",
            ],
        )
        earnings = max_(raw_earnings, 0)
        income_change = person("relative_income_change", period)
        return earnings * income_change * person("income_elasticity", period)
