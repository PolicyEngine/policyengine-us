from policyengine_us.model_api import *


class roth_ira_contributions(Variable):
    value_type = float
    entity = Person
    label = "Roth IRA contributions"
    unit = USD
    documentation = (
        "Roth IRA contributions after applying the combined traditional "
        "and Roth IRA contribution limit. If desired IRA contributions exceed "
        "the limit, PolicyEngine preserves desired allocation shares by "
        "scaling traditional and Roth IRA contributions proportionally."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#b",
        "https://www.law.cornell.edu/uscode/text/26/408A#c_2",
    )

    def formula(person, period, parameters):
        desired = person("roth_ira_contributions_desired", period)
        scale = person("ira_contribution_scale", period)
        return desired * scale
