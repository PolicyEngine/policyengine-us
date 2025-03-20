from policyengine_us.model_api import *


class ma_tafdc_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to income"
    definition_period = MONTH
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        income = add(
            spm_unit,
            period,
            [
                "ma_tafdc_partially_disregarded_earned_income",
                "ma_tafdc_unearned_income",
            ],
        )
        payment_standard = spm_unit("ma_tafdc_payment_standard", period)
        return income < payment_standard
