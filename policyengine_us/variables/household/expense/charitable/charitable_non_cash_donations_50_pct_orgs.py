from policyengine_us.model_api import *


class charitable_non_cash_donations_50_pct_orgs(Variable):
    value_type = float
    entity = Person
    label = "Charitable non-cash donations to 50% limit organizations"
    unit = USD
    documentation = (
        "Non-cash ordinary (non-capital-gain) charitable donations to "
        "50-percent limit organizations described in 26 U.S. Code § 170(b)(1)(A). "
        "These are subject to a 50% AGI ceiling under 26 U.S. Code § 170(b)(1)(A)."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_A"
