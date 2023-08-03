from policyengine_us.model_api import *


class average_home_energy_use_in_state(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    documentation = (
        "Average energy use per home in household's state, in kilowatt hours"
    )
    label = "Average energy use per in state"
