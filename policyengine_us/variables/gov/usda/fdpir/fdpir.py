from policyengine_us.model_api import *


class fdpir(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Food Distribution Program on Indian Reservations"
    unit = USD
    documentation = (
        "Benefit value of the Food Distribution Program on Indian Reservations"
    )
