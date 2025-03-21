from policyengine_us.model_api import *


class ma_tafdc(Variable):
    value_type = float
    unit = USD
    entity = SPMUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = "ma_tafdc_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("ma_tafdc_payment_standard", period)
        countable_income = spm_unit("ma_tafdc_countable_income", period)
        clothing_allowance = spm_unit.sum(
            spm_unit.members("ma_tafdc_clothing_allowance", period)
        )
        infant_benefit = spm_unit.sum(
            spm_unit.members("ma_tafdc_infant_benefit", period)
        )

        return (
            max_(0, payment_standard - countable_income)
            + clothing_allowance
            + infant_benefit
        )
