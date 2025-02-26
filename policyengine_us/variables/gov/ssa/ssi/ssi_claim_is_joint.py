from policyengine_us.model_api import *


class ssi_claim_is_joint(Variable):
    value_type = bool
    entity = Person
    label = "SSI claim is joint"
    definition_period = YEAR

    def formula(person, period, parameters):
        both_eligible = person("ssi_marital_both_eligible", period)
        is_eligible = person("is_ssi_eligible_individual", period)
        has_ineligible_spouse = person.marital_unit.any(
            person("is_ssi_ineligible_spouse", period)
        )

        # A claim is joint if either:
        # 1. Both spouses are eligible, or
        # 2. One spouse is eligible and the other is ineligible (deeming applies)
        return both_eligible | (is_eligible & has_ineligible_spouse)
