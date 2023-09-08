from policyengine_us.model_api import *


class ca_tanf_countable_income_recipient(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Countable Income for Computing Payments"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ca.cdss.tanf.income.disregards.recipient
        earned = spm_unit("ca_tanf_earned_income", period)
        db_unearned = spm_unit("ca_tanf_db_unearned_income", period)
        unearned = spm_unit("ca_tanf_unearned_income", period)

        countable_db_unearned = max_(db_unearned - p.flat, 0)
        countable_earned = max_(earned - max_(p.flat - db_unearned, 0), 0) * (
            1 - p.percentage
        )

        return countable_earned + countable_db_unearned + unearned
