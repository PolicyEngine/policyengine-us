from policyengine_us.model_api import *


class ca_tanf_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-101_Income_Definitions%2F44-101_Income_Definitions.htm%23Definitionsbc-4&rhtocid=_3_1_6_0_3"

    adds = "gov.states.ca.cdss.tanf.cash.income.sources.earned"
