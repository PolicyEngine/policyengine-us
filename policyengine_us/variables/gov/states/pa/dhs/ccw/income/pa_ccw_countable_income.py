from policyengine_us.model_api import *


class pa_ccw_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania CCW countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=59"

    adds = "gov.states.pa.dhs.ccw.income.countable_income.sources"
