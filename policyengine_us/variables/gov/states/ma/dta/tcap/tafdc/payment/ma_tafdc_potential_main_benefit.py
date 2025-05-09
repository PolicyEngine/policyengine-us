from policyengine_us.model_api import *


class ma_tafdc_potential_main_benefit(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) potential main benefit"
    definition_period = MONTH
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = "ma_tafdc_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("ma_tafdc_payment_standard", period)
        countable_income = spm_unit(
            "ma_tafdc_applicable_income_grant_amount", period
        )
        return max_(0, payment_standard - countable_income)
