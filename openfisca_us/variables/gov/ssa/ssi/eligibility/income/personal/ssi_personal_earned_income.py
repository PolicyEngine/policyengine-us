from openfisca_us.model_api import *


class ssi_personal_earned_income(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income (personal)"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables("ssa.ssi.income.sources.earned")