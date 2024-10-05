from policyengine_us.model_api import *


class ssi_earned_income(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income"
    unit = USD
    definition_period = YEAR

    adds = "gov.ssa.ssi.income.sources.earned"
