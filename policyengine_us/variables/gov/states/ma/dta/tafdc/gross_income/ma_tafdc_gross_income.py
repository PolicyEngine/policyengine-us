from policyengine_us.model_api import *


class ma_tafdc_gross_income(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) gross income"
    definition_period = MONTH
    reference = "https://www.masslegalservices.org/content/73-how-much-income-can-you-have-and-still-qualify-tafdc"
    defined_for = StateCode.MA

    adds = [
        "ma_tafdc_earned_income",
        "ma_tafdc_unearned_income",
    ]
