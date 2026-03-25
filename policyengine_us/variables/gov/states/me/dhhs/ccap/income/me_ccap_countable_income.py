from policyengine_us.model_api import *


class me_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maine CCAP countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=13"

    adds = "gov.states.me.dhhs.ccap.income.countable_income.sources"
