from policyengine_us.model_api import *


class ca_tanf_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Other Unearned Income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-101_Income_Definitions%2F44-101_Income_Definitions.htm%23Policybc-2&rhtocid=_3_1_6_0_1"
    """
    descripton: Unearned Income - Income that is not earned or disability-based income. 
    reference:
      - title: Los Angeles Department of Public Social Services E-Policy | Income Definitions
        href: http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-101_Income_Definitions%2F44-101_Income_Definitions.htm%23Policybc-2&rhtocid=_3_1_6_0_1
    """