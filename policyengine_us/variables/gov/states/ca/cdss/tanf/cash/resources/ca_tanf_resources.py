from policyengine_us.model_api import *


class ca_tanf_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Resources"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F42-200_Property%2F42-200_Property.htm%23Policybc-2&rhtocid=_3_1_2_0_1"

    adds = "gov.states.ca.cdss.tanf.cash.resources.sources"
