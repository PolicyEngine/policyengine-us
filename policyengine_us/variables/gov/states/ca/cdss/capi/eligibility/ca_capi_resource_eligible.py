from policyengine_us.model_api import *


class ca_capi_resource_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CAPI resource eligible"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://www.cdss.ca.gov/Portals/9/CAPI/CAPI_Regulations-Accessible.pdf"

    def formula(spm_unit, period, parameters):
        resources = spm_unit("ca_capi_resources", period)
        p = parameters(period).gov.states.ca.cdss.capi.resources
        married = spm_unit("spm_unit_is_married", period)
        resource_limit = where(married, p.limit.couple, p.limit.single)
        return resources <= resource_limit
