from openfisca_us.model_api import *


class ssi_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "SSI countable resources"
    unit = USD
    definition_period = YEAR
