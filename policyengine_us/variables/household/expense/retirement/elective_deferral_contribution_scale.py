from policyengine_us.model_api import *


class elective_deferral_contribution_scale(Variable):
    value_type = float
    entity = Person
    label = "401(k) and 403(b) elective deferral contribution scale"
    unit = "/1"
    documentation = (
        "Scale factor applied to desired 401(k) and 403(b) deferrals when "
        "they exceed the combined elective deferral limit. This preserves "
        "desired allocation shares rather than prioritizing any deferral type."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/402#g"

    def formula(person, period, parameters):
        total_desired = add(
            person,
            period,
            [
                "traditional_401k_contributions_desired",
                "roth_401k_contributions_desired",
                "traditional_403b_contributions_desired",
                "roth_403b_contributions_desired",
            ],
        )
        return min_(
            person("elective_deferral_limit", period) / max_(total_desired, 1),
            1,
        )
