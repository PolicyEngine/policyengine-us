from openfisca_us.model_api import *


class average_energy_use_per_home_in_state(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    documentation = (
        "Average energy use per home in household's state, in kilowatt hours"
    )
    label = "Average energy use per in state"
