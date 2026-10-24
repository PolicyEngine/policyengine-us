from policyengine_us.model_api import *


class ca_capi_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "California CAPI eligible person"
    definition_period = YEAR
    defined_for = StateCode.CA
    # PDF pages 10, 47
    reference = (
        "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf#page=10"
    )

    def formula(person, period, parameters):
        # Both members of a couple can be eligible (MPP 49-055.4).
        aged_blind_disabled = person("is_ssi_aged_blind_disabled", period)
        immigration_status = person("immigration_status", period)
        is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
        is_qualified_noncitizen = person("is_ssi_qualified_noncitizen", period)

        return aged_blind_disabled & ~is_citizen & ~is_qualified_noncitizen
