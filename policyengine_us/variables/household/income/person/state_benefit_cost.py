from policyengine_us.model_api import *


class state_benefit_cost(Variable):
    value_type = float
    entity = Person
    label = "State benefit cost attributed to this person"
    documentation = (
        "Sum of the state-government portion of benefit expenditures for "
        "programs this person is enrolled in. Grows as programs gain "
        "federal/state attribution — currently Medicaid and CHIP."
    )
    unit = USD
    definition_period = YEAR
    adds = ["medicaid_state_cost", "chip_state_cost"]
