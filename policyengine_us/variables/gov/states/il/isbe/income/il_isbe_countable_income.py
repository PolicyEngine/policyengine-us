from policyengine_us.model_api import *


class il_isbe_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois ISBE countable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.isbe.net/Documents/Income-Verification-FAQ.pdf"
    defined_for = StateCode.IL

    adds = "gov.states.il.isbe.income.countable_sources"
