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
        raw = person("uncapped_roth_403b_contributions", period)
        total_desired = add(
            person,
            period,
            [
                "uncapped_traditional_401k_contributions",
                "uncapped_roth_401k_contributions",
                "uncapped_traditional_403b_contributions",
                "uncapped_roth_403b_contributions",
            ],
        )
        # Behavioral assumption: no deferral type is prioritized. Preserve
        # desired allocation shares by applying one scale factor to all 401(k)
        # and 403(b) deferrals subject to this combined limit.
        scale = min_(
            person("elective_deferral_limit", period) / max_(total_desired, 1), 1
        )
        return raw * scale
