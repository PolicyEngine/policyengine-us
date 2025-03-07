from policyengine_us.model_api import *


class ma_tafdc(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = "https://www.mass.gov/how-to/transitional-aid-to-families-with-dependent-children-tafdc"
    defined_for = "ma_tafdc_eligible"

    def formula(tax_unit, period, parameters):
        payment_standard = tax_unit("ma_tafdc_payment_standard", period)
        gross_income = tax_unit("ma_tafdc_gross_income", period)
        clothing_allowance = tax_unit.sum(
            tax_unit.members("ma_tafdc_clothing_allowance", period)
        )
        return max_(0, payment_standard - gross_income) + clothing_allowance
