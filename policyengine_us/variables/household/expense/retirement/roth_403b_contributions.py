from policyengine_us.model_api import *


class roth_403b_contributions(Variable):
    value_type = float
    entity = Person
    label = "Roth 403(b) contributions"
    unit = USD
    documentation = (
        "Roth 403(b) contributions after applying the combined 401(k) and "
        "403(b) elective deferral limit. If desired deferrals exceed the "
        "limit, PolicyEngine preserves desired allocation shares by scaling "
        "each deferral in the shared limit group proportionally."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/402#g"

    def formula(person, period, parameters):
        desired = person("roth_403b_contributions_desired", period)
        scale = person("elective_deferral_contribution_scale", period)
        return desired * scale
