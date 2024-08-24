from policyengine_us.model_api import *


class ma_eaedc_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC umearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    adds = "gov.states.ma.dta.tcap.eaedc.income.unearned"
