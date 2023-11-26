from policyengine_us.model_api import *


class ca_tanf_recipient_financial_test(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Recipient Financial Test"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-111_23_Earned_Income_Disregards%2F44-111_23_Earned_Income_Disregards.htm%23Policybc-2&rhtocid=_3_1_6_2_1"

    def formula(spm_unit, period, parameters):
        maximum_payment = spm_unit("ca_tanf_maximum_payment", period)
        countable_income = spm_unit(
            "ca_tanf_countable_income_recipient", period
        )

        return countable_income < maximum_payment
