from policyengine_us.model_api import *


class ca_tanf_region1(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Region 1"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-212_Minimum_Basic_Standard_of_Adequate_Care%2F44-212_Minimum_Basic_Standard_of_Adequate_Care.htm%23Definitionsbc-4&rhtocid=_3_1_7_20_3"

    def formula(spm_unit, period, parameters):
        county = spm_unit.household("county_str", period)
        region1_counties = parameters(
            period
        ).gov.states.ca.cdss.tanf.region1_counties
        return county in region1_counties
