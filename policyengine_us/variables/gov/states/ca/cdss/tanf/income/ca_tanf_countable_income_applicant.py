from policyengine_us.model_api import *


class ca_tanf_countable_income_applicant(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Countable Income for Eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.income.disregards.applicant
        countable_earned = max_(
            spm_unit("ca_tanf_earned_income", period) - p.flat, 0
        )
        db_unearned = spm_unit("ca_tanf_db_unearned_income", period)
        unearned = spm_unit("ca_tanf_unearned_income", period)

        return countable_earned + db_unearned + unearned
