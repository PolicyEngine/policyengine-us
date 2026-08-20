from policyengine_us.model_api import *


class medicaid_ltss_home_market_value(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS home market value"
    unit = USD
    quantity_type = STOCK
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Explicit current market value of the home used in the separate "
        "Medicaid LTSS home-equity payment-bar calculation. Home equity is "
        "not treated as an ordinary countable resource by this input."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/1396p#f"
