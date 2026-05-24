from policyengine_us.model_api import *


class capped_roth_ira_contributions(Variable):
    value_type = float
    entity = Person
    label = "Capped Roth IRA contributions"
    unit = USD
    documentation = (
        "Roth IRA contributions after applying the combined traditional "
        "and Roth IRA contribution limit."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b",
        "https://www.law.cornell.edu/uscode/text/26/408A#c_2",
    )

    def formula(person, period, parameters):
        raw = person("uncapped_roth_ira_contributions", period)
        total_desired = add(
            person,
            period,
            [
                "uncapped_traditional_ira_contributions",
                "uncapped_roth_ira_contributions",
            ],
        )
        scale = min_(
            person("ira_contribution_limit", period) / max_(total_desired, 1), 1
        )
        return raw * scale
