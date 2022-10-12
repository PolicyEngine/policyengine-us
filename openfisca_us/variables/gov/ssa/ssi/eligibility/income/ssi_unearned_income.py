from policyengine_us.model_api import *


class ssi_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables("gov.ssa.ssi.income.sources.unearned")
