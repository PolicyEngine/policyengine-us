from policyengine_us.model_api import *


class charitable_capital_gain_donations_non_50_pct_orgs(Variable):
    value_type = float
    entity = Person
    label = "Charitable capital gain property donations to non-50% limit organizations"
    unit = USD
    documentation = (
        "Charitable donations of capital gain property (such as long-term "
        "appreciated stock) to organizations other than 50-percent limit "
        "organizations, such as private non-operating foundations. "
        "Contributions 'for the use of' an organization also belong in "
        "this non-50% input (IRS Pub 526 Worksheet 2, lines 4–5). "
        "These are subject to a 20% AGI ceiling under 26 U.S. Code § 170(b)(1)(D)."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_D"
