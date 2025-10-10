from policyengine_us.model_api import *


class tx_tanf_eligible_child(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible child for Texas TANF (included in certified group)"
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-104",
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-220-tanf",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        # Child must meet age/demographic requirements
        age_eligible = person("tx_tanf_age_eligible_child", period)

        # And meet inclusion requirements (immigration eligible, not receiving SSI)
        inclusion_requirements = person(
            "tx_tanf_categorically_eligible_person", period
        )

        return age_eligible & inclusion_requirements
