from policyengine_us.model_api import *


class ma_tafdc_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-000"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        total_countable_income = spm_unit(
            "ma_tafdc_applicable_income_for_financial_eligibility", period
        )
        payment_standard = spm_unit("ma_tafdc_payment_standard", period)

        return total_countable_income < payment_standard
