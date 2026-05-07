from policyengine_us.model_api import *


class md_tca_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    adds = [
        "md_tca_countable_earned_income",
        "tanf_gross_unearned_income",
    ]
