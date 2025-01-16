from policyengine_us.model_api import *


class ca_capi_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CAPI eligible"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf"

    def formula(spm_unit, period, parameters):
        resource_eligible = spm_unit("ca_capi_resource_eligible", period)
        income_eligible = spm_unit("ca_capi_income_eligible", period)
        person = spm_unit.members
        eligible_person = person("ca_capi_eligible_person", period)
        eligible_person_present = spm_unit.any(eligible_person)
        return resource_eligible & income_eligible & eligible_person_present
