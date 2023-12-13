from policyengine_us.model_api import *


class ca_tanf_resources_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for the California CalWORKs based on the available resources"
    )
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F42-200_Property%2F42-200_Property.htm%23Policybc-2&rhtocid=_3_1_2_0_1"

    def formula(spm_unit, period, parameters):
        resources = spm_unit("ca_tanf_resources", period)
        limit = spm_unit("ca_tanf_resources_limit", period)
        return resources <= limit
