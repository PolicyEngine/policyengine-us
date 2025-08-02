from policyengine_us.model_api import *


class sc_tanf_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina TANF unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    adds = "gov.states.sc.tanf.income.unearned"
