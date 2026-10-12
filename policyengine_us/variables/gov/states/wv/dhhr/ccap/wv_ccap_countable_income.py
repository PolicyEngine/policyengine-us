from policyengine_us.model_api import *


class wv_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia CCAP countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.WV
    reference = "https://bfa.wv.gov/media/6766/download?inline#page=51"

    adds = "gov.states.wv.dhhr.ccap.income.countable_income.sources"
