from policyengine_us.model_api import *


class al_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama income tax before refundable credits"
    defined_for = StateCode.AL
    unit = USD
    definition_period = YEAR
    # The Code of Alabama 1975 Section 40-18-5
    reference = " https://alisondb.legislature.state.al.us/alison/CodeOfAlabama/1975/Coatoc.htm"

    def formula(tax_unit, period, parameters):
        tax_before_credits = tax_unit(
            "al_income_tax_before_non_refundable_credits", period
        )
        non_refundable_credits = tax_unit("al_non_refundable_credits", period)
        return max_(tax_before_credits - non_refundable_credits, 0)
