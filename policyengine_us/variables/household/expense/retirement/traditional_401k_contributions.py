from policyengine_us.model_api import *


class traditional_401k_contributions(Variable):
    value_type = float
    entity = Person
    label = "Traditional 401(k) contributions"
    unit = USD
    documentation = (
        "Traditional 401(k) contributions after applying the combined "
        "401(k) and 403(b) elective deferral limit."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/402#g"

    def formula(person, period, parameters):
        raw = person("uncapped_traditional_401k_contributions", period)
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
        scale = min_(
            person("elective_deferral_limit", period) / max_(total_desired, 1), 1
        )
        return raw * scale
