from openfisca_us.model_api import *


class early_withdrawal_penalty(Variable):
    value_type = float
    entity = Person
    label = "Early savings withdrawal penalty"
    unit = USD
    documentation = "Penalties paid due to early withdrawal of savings."
    definition_period = YEAR
