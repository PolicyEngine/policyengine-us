from policyengine_us.model_api import *


class pa_tanf_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA

    # adds = "gov.states.dc.dhs.tanf.income.earned"
