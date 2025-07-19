from policyengine_us.model_api import *


class pa_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "PA TANF gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PA

    adds = "gov.states.pa.tanf.income.pa_tanf_unearned_income"
