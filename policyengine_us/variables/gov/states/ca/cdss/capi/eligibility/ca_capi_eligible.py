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
        has_eligible_person = (
            add(spm_unit, period, ["ca_capi_eligible_person"]) > 0
        )
        return resource_eligible & income_eligible & has_eligible_person
