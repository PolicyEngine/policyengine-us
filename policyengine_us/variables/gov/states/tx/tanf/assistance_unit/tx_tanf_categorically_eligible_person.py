from policyengine_us.model_api import *


class tx_tanf_categorically_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Categorically eligible person for Texas TANF"
    reference = (
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-201",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-104",
    )
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        immigration_eligible = person("is_citizen_or_legal_immigrant", period)
        ssi = person("ssi", period)

        return immigration_eligible & (ssi == 0)
