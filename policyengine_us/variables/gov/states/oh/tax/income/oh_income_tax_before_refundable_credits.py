from policyengine_us.model_api import *


class oh_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        itax_before_credits = tax_unit(
            "oh_income_tax_before_non_refundable_credits", period
        )
        nonrefundable_credits = tax_unit("oh_non_refundable_credits", period)
        return max_(0, itax_before_credits - nonrefundable_credits)
