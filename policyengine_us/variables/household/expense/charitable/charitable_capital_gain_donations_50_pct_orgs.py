from policyengine_us.model_api import *


class charitable_capital_gain_donations_50_pct_orgs(Variable):
    value_type = float
    entity = Person
    label = "Charitable capital gain property donations to 50% limit organizations"
    unit = USD
    documentation = (
        "Charitable donations of capital gain property (such as long-term "
        "appreciated stock or real estate) to 50-percent limit organizations "
        "described in 26 U.S. Code § 170(b)(1)(A). These are subject to a "
        "30% AGI ceiling under 26 U.S. Code § 170(b)(1)(C)(i)."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_C"
