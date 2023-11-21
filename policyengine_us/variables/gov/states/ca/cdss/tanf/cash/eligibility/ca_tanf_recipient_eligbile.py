from policyengine_us.model_api import *


class ca_tanf_recipient_eligbile(Variable):
    value_type = bool
    entity = SPMUnit
    label = "California CalWORKs Recipient Financial Eligibility"
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-111_23_Earned_Income_Disregards%2F44-111_23_Earned_Income_Disregards.htm%23Policybc-2&rhtocid=_3_1_6_2_1"

    def formula(spm_unit, period, parameters):
        tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        applicant_eligible = spm_unit("ca_tanf_applicant_eligible", period)
        maximum_payment = spm_unit("ca_tanf_maximum_payment", period)
        countable_income = spm_unit(
            "ca_tanf_countable_income_recipient", period
        )

        return (tanf_enrolled | applicant_eligible) & (
            maximum_payment > countable_income
        )
