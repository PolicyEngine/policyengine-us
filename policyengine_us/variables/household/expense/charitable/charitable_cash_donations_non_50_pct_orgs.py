from policyengine_us.model_api import *


class charitable_cash_donations_non_50_pct_orgs(Variable):
    value_type = float
    entity = Person
    label = "Charitable cash donations to non-50% limit organizations"
    unit = USD
    documentation = (
        "Cash charitable donations to organizations other than "
        "50-percent limit organizations described in "
        "26 U.S. Code § 170(b)(1)(A), such as private non-operating "
        "foundations, veterans organizations, and fraternal domestic "
        "societies. These are subject to a 30% AGI ceiling under "
        "26 U.S. Code § 170(b)(1)(B)."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_B"
