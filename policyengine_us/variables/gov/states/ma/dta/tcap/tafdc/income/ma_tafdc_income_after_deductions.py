from policyengine_us.model_api import *


class ma_tafdc_income_after_deductions(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) earned income after deductions"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-280"
    )
    defined_for = StateCode.MA

    adds = [
        "ma_tafdc_earned_income_after_deductions",
        "ma_tafdc_countable_unearned_income",
    ]
