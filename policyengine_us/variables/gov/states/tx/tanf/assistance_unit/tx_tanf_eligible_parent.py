from policyengine_us.model_api import *


class tx_tanf_eligible_parent(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible parent for Texas TANF (included in certified group)"
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-104",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-102",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        # Per § 372.104, parents living in household must be included in certified group
        is_parent = person("is_tax_unit_head_or_spouse", period)

        # Must meet inclusion requirements
        inclusion_requirements = person(
            "tx_tanf_categorically_eligible_person", period
        )

        return is_parent & inclusion_requirements
