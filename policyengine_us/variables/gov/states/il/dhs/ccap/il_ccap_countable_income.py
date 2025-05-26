from policyengine_us.model_api import *


class il_ccap_countable_income(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Illinois Child Care Assistance Program (CCAP) countable income"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-50.235"
    defined_for = StateCode.IL

    adds = "gov.states.il.dhs.ccap.income.countable_income.sources"
