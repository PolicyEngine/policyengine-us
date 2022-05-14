from openfisca_us.model_api import *


class short_term_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Short-term capital gains"
    unit = USD
    definition_period = YEAR
