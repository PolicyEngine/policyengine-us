from policyengine_us.model_api import *


class ca_tanf_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Exempt Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-315_CalWORKs_Maximum_Aid_Payment_Levels%2F44-315_CalWORKs_Maximum_Aid_Payment_Levels.htm%23Policybc-2&rhtocid=_3_1_8_4_1"

    adds = "gov.states.ca.cdss.tanf.cash.exempt"
