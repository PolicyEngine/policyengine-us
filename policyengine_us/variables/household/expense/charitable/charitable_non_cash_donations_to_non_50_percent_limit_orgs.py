from policyengine_us.model_api import *


class charitable_non_cash_donations_to_non_50_percent_limit_orgs(Variable):
    value_type = float
    entity = Person
    label = "Charitable non-cash donations to non-50% limit organizations"
    unit = USD
    documentation = (
        "Non-cash charitable donations to organizations other than "
        "50-percent limit organizations described in 26 USC 170(b)(1)(A), "
        "such as private non-operating foundations. These donations are "
        "subject to a 30% AGI ceiling under 26 USC 170(b)(1)(B), rather "
        "than the 50% ceiling for 50-percent limit organizations."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_B"
