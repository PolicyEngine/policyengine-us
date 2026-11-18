from policyengine_us.model_api import *


class modeled_state_unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "modeled state unemployment compensation"
    unit = USD
    documentation = (
        "Unemployment compensation computed from the modeled state "
        "unemployment insurance programs. Each program counts from the "
        "first year its implementation is verified."
    )
    definition_period = YEAR
    adds = "gov.states.household.modeled_state_unemployment_compensation"
