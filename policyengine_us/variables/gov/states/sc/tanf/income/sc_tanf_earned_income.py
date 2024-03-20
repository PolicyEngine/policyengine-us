from policyengine_us.model_api import *


class sc_tanf_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "SC TANF earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    adds = "gov.states.sc.tanf.income.earned"
