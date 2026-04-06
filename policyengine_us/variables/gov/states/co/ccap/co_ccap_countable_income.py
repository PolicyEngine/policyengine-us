from policyengine_us.model_api import *


class co_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Colorado Child Care Assistance Program countable income"
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=22"
    unit = USD
    defined_for = StateCode.CO

    adds = "gov.states.co.ccap.income.countable_income.sources"
