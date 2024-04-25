from policyengine_us.model_api import *


class al_tanf_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alabama TANF unearned income"
    defined_for = StateCode.AL
    definition_period = YEAR

    adds = "gov.states.al.dhs.tanf.income.unearned"
