from policyengine_us.model_api import *


class ira_contribution_scale(Variable):
    value_type = float
    entity = Person
    label = "IRA contribution scale"
    unit = "/1"
    documentation = (
        "Scale factor applied to desired traditional and Roth IRA "
        "contributions when they exceed the combined IRA contribution limit. "
        "This preserves desired allocation shares rather than prioritizing "
        "either IRA type."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b",
        "https://www.law.cornell.edu/uscode/text/26/408A#c_2",
    )

    def formula(person, period, parameters):
        total_desired = add(
            person,
            period,
            [
                "traditional_ira_contributions_desired",
                "roth_ira_contributions_desired",
            ],
        )
        return min_(
            person("ira_contribution_limit", period) / max_(total_desired, 1),
            1,
        )
