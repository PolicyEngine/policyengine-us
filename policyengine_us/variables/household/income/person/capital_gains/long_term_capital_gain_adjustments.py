from policyengine_us.model_api import *


class long_term_capital_gain_adjustments(Variable):
    value_type = float
    entity = Person
    label = "long-term capital gain amounts computed from detailed inputs"
    unit = USD
    definition_period = YEAR
    adds = [
        "section_1256_long_term_gain",
        "home_sale_taxable_gain",
        "investment_lot_long_term_gain",
    ]
