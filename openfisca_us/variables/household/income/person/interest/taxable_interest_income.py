from openfisca_us.model_api import *


class taxable_interest_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable interest income"
    unit = USD
    documentation = "Income from interest that is taxable."
    definition_period = YEAR
