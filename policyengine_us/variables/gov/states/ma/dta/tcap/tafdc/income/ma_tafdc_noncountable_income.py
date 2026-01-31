from policyengine_us.model_api import *


class ma_tafdc_noncountable_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts TAFDC noncountable income"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-250"
    defined_for = StateCode.MA

    adds = "gov.states.ma.dta.tcap.tafdc.income.noncountable.sources"
