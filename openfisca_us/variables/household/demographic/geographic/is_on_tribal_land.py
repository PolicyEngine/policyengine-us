from openfisca_us.model_api import *


class is_on_tribal_land(Variable):
    value_type = bool
    entity = Household
    definition_period = ETERNITY
    label = "Is on tribal land"
    documentation = "Whether the household is on tribal land"
