from policyengine_us.model_api import *


class charitable_non_cash_donations_non_50_pct_orgs(Variable):
    value_type = float
    entity = Person
    label = "Charitable non-cash donations to non-50% limit organizations"
    unit = USD
    documentation = (
        "Non-cash charitable donations to organizations other than "
        "50-percent limit organizations described in "
        "26 U.S. Code § 170(b)(1)(A), such as private non-operating "
        "foundations. Contributions 'for the use of' an organization "
        "also belong in this non-50% input (IRS Pub 526 Worksheet 2, line 5). "
        "These are subject to a 30% AGI ceiling under 26 U.S. Code § 170(b)(1)(B)."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_B"
