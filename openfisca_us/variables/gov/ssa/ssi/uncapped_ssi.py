from openfisca_us.model_api import *


class uncapped_ssi(Variable):
    value_type = float
    entity = MaritalUnit
    label = "Uncapped SSI"
    unit = USD
    documentation = "Maximum SSI, less countable income (can be below zero)."
    definition_period = YEAR

    def formula(marital_unit, period, parameters):
        person = marital_unit.members
        abd = person("is_ssi_aged_blind_disabled", period)
        amount = marital_unit("maximum_ssi", period)
        personal_income = person("ssi_countable_income", period)
        countable_income = marital_unit.sum(personal_income * abd)
        return amount - countable_income
