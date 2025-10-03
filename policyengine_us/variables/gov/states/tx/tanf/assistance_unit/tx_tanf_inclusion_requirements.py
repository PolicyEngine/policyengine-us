from policyengine_us.model_api import *


class tx_tanf_inclusion_requirements(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Meets Texas TANF certified group inclusion requirements"
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-201",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-104",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        # Requirements for being included in the certified group
        # Cannot receive both SSI and TANF
        immigration_eligible = person(
            "tx_tanf_immigration_status_eligible_person", period
        )
        ssi = person("ssi", period)

        return immigration_eligible & (ssi == 0)
