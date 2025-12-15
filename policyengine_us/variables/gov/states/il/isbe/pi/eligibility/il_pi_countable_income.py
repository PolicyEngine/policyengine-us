from policyengine_us.model_api import *


class il_pi_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois PI countable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.isbe.net/Documents/69-72_hshld_income.pdf"
    defined_for = StateCode.IL

    adds = "gov.states.il.isbe.pi.eligibility.income.countable_sources"
