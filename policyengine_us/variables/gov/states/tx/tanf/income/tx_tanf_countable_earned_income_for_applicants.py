from policyengine_us.model_api import *


class tx_tanf_countable_earned_income_for_applicants(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable earned income for applicants (with 1/3 disregard)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-605",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        countable_earned = spm_unit("tx_tanf_countable_earned_income", period)
        p = parameters(period).gov.states.tx.tanf.income

        applicant_disregard = (
            countable_earned * p.applicant_earned_income_fraction
        )

        return max_(countable_earned - applicant_disregard, 0)
