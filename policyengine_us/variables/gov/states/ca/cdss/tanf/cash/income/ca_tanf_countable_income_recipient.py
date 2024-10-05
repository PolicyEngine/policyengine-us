from policyengine_us.model_api import *


class ca_tanf_countable_income_recipient(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs countable income for payment computation"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "http://epolicy.dpss.lacounty.gov/epolicy/epolicy/server/general/projects_responsive/ePolicyMaster/index.htm?&area=general&type=responsivehelp&ctxid=&project=ePolicyMaster#t=mergedProjects%2FCalWORKs%2FCalWORKs%2F44-111_23_Earned_Income_Disregards%2F44-111_23_Earned_Income_Disregards.htm%23Policybc-2&rhtocid=_3_1_6_2_1"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.cash.income.disregards.recipient
        earned = spm_unit("ca_tanf_earned_income", period) / MONTHS_IN_YEAR
        db_unearned = (
            spm_unit("ca_tanf_db_unearned_income", period)
        ) / MONTHS_IN_YEAR
        other_unearned = (
            spm_unit("ca_tanf_other_unearned_income", period)
        ) / MONTHS_IN_YEAR

        # Flat exlusion only applies to disability-based unearned income and earned income.
        countable_db_unearned = max_(db_unearned - p.flat, 0)
        remaining_flat_exclusion = max_(p.flat - db_unearned, 0)
        countable_earned = max_(earned - remaining_flat_exclusion, 0) * (
            1 - p.percentage
        )

        return (
            countable_earned + countable_db_unearned + other_unearned
        ) * MONTHS_IN_YEAR
