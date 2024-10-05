from policyengine_us.model_api import *


class ma_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section4"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        tax_before_credits = tax_unit("ma_income_tax_before_credits", period)
        non_refundable_credits = tax_unit("ma_non_refundable_credits", period)
        return max_(tax_before_credits - non_refundable_credits, 0)
