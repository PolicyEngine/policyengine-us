from policyengine_us.model_api import *


class co_tanf_countable_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado TANF countable gross earned income"
    unit = USD
    definition_period = YEAR

    adds = "gov.states.co.cdhs.tanf.income.earned"
