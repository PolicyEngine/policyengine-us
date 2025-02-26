from policyengine_us.model_api import *


class ma_eaedc_total_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Massachusetts EAEDC earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA

    adds = "gov.states.ma.dta.tcap.eaedc.income.earned"
