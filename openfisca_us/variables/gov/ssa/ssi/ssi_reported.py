from openfisca_us.model_api import *


class ssi_reported(Variable):
    value_type = float
    entity = Person
    label = "SSI (reported)"
    definition_period = YEAR
