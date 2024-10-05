from policyengine_us.model_api import *


class ca_tanf_countable_income_applicant(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Countable Income for Eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-111_23_Earned_Income_Disregards%2F44-111_23_Earned_Income_Disregards.htm%23Policybc-2&rhtocid=_3_1_6_2_1"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.cash.income.disregards.applicant
        yearly_disregard = p.flat * MONTHS_IN_YEAR
        countable_earned = max_(
            spm_unit("ca_tanf_earned_income", period) - yearly_disregard, 0
        )
        db_unearned = spm_unit("ca_tanf_db_unearned_income", period)
        other_unearned = spm_unit("ca_tanf_other_unearned_income", period)

        return countable_earned + db_unearned + other_unearned
