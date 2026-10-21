from policyengine_us.model_api import *


class charitable_capital_gain_donations(Variable):
    value_type = float
    entity = Person
    label = "Charitable capital gain donations"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Total charitable donations of capital gain property (such as long-term "
        "appreciated stock or real estate)."
    )
    adds = [
        "charitable_capital_gain_donations_50_pct_orgs",
        "charitable_capital_gain_donations_non_50_pct_orgs",
    ]
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_C"
