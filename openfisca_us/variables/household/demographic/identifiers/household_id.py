from openfisca_us.model_api import *


class household_id(Variable):
    value_type = float
    entity = Household
    label = "Unique reference for this household"
    definition_period = ETERNITY
