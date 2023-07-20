from policyengine_us.model_api import *


class or_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html"  # 316.695 (1)(d)
    defined_for = StateCode.OR

    adds = ["itemized_deductions_less_salt", "capped_property_taxes"]
