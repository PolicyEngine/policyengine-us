from policyengine_us.model_api import *


class wa_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF countable income"
    unit = USD
    definition_period = MONTH
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0165"
    defined_for = StateCode.WA

    adds = [
        "wa_tanf_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
