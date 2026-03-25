from policyengine_us.model_api import *


class ma_tafdc_ssi_recipient_income_exclusion(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts TAFDC SSI recipient income exclusion"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-250"
    defined_for = StateCode.MA

    adds = [
        "ma_tafdc_ssi_recipient_earned_income_exclusion",
        "ma_tafdc_ssi_recipient_unearned_income_exclusion",
    ]
