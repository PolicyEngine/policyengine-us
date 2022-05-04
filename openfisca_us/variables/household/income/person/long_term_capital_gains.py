from openfisca_us.model_api import *


class long_term_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Long-term capital gains"
    unit = USD
    definition_period = YEAR
