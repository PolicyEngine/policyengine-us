from policyengine_us.model_api import *
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    calculate_substitution_lsr_effect,
)


class substitution_elasticity_lsr(Variable):
    value_type = float
    entity = Person
    label = "substitution elasticity of labor supply response"
    unit = "/1"
    definition_period = YEAR
    requires_computation_after = "labor_supply_behavioral_response"

    def formula(person, period, parameters):
        return calculate_substitution_lsr_effect(person, period, parameters)
