from policyengine_us.model_api import *


class ca_capi_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "California CAPI eligible person"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf"

    def formula(person, period, parameters):
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        is_ssi_eligible_spouse = person("is_ssi_eligible_spouse", period)
        immigration_status = person("immigration_status", period)
        is_citizen = (
            immigration_status == immigration_status.possible_values.CITIZEN
        )

        return aged_blind_disabled & ~is_ssi_eligible_spouse & ~is_citizen
