from policyengine_us.model_api import *


class ma_ccfa_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = (
        "Massachusetts Child Care Financial Assistance (CCFA) countable income"
    )
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "Policy Guide Chapter 4.1"

    adds = "gov.states.ma.eec.ccfa.income.countable_income.sources"
