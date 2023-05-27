from policyengine_us.model_api import *


class nc_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        tax_before_credits = tax_unit("nc_income_tax_before_credits", period)
        # North Carolina does not allow for any refundable credits
        credits = tax_unit("nc_non_refundable_credits", period)
        return max_((tax_before_credits - credits), 0)
