from openfisca_us.model_api import *


class ssi_countable_income(Variable):
    value_type = float
    entity = Person
    label = "SSI countable income"
    unit = USD
    definition_period = YEAR

