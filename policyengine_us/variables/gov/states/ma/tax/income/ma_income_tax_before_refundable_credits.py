from policyengine_us.model_api import *


class ma_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    reference = "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section4"
    defined_for = StateCode.MA
    adds = ["ma_income_tax_before_credits"]
