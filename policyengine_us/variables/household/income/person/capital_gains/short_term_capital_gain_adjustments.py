from policyengine_us.model_api import *


class short_term_capital_gain_adjustments(Variable):
    value_type = float
    entity = Person
    label = "short-term capital gain amounts computed from detailed inputs"
    unit = USD
    definition_period = YEAR
    adds = [
        "section_1256_short_term_gain",
        "home_sale_taxable_short_term_gain",
        "investment_lot_short_term_gain",
    ]
