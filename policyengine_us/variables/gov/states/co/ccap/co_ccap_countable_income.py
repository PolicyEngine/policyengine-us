from policyengine_us.model_api import *


class co_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "Colorado Child Care Assitance Program Countable Income"
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=22"
    unit = USD
    # TODO: Use income components from the manual.
    adds = ["snap_earned_income", "snap_unearned_income"]
