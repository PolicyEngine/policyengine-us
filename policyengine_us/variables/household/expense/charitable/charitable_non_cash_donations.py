from policyengine_us.model_api import *


class charitable_non_cash_donations(Variable):
    value_type = float
    entity = Person
    label = "Charitable donations (non-cash)"
    unit = USD
    definition_period = YEAR
    adds = [
        "charitable_non_cash_donations_50_pct_orgs",
        "charitable_non_cash_donations_non_50_pct_orgs",
    ]
