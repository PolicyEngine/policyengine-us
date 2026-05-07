from policyengine_us.model_api import *


class sd_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Dakota TANF countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://sdlegislature.gov/Rules/Administrative/67:10:03:04"
    defined_for = StateCode.SD

    # NOTE: Result will never go below 0 because child_support_received
    # is already included in tanf_gross_unearned_income.
    adds = ["tanf_gross_unearned_income"]
    subtracts = ["child_support_received"]
