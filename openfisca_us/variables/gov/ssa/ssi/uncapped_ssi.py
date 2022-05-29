from openfisca_us.model_api import *


class uncapped_ssi(Variable):
    value_type = float
    entity = Person
    label = "Uncapped SSI"
    unit = USD
    documentation = "Maximum SSI, less countable income (can be below zero)."
    definition_period = YEAR

    def formula(person, period, parameters):
        amount = person("ssi_amount_if_eligible", period)
        countable_income = person("ssi_countable_income", period)
        return amount - countable_income
