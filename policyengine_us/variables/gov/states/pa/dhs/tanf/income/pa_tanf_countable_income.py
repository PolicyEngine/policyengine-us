from policyengine_us.model_api import *


class pa_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/chap183toc.html"

    adds = [
        "pa_tanf_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
