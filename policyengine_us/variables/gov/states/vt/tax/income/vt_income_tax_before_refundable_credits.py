from policyengine_us.model_api import *


class vt_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        itax_before_credits = tax_unit("vt_income_tax_before_credits", period)
        nonrefundable_credits = tax_unit("vt_nonrefundable_credits", period)
        return max_(0, itax_before_credits - nonrefundable_credits)
