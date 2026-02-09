from policyengine_us.model_api import *


class ia_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.tanf.income
        earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Per IAC 441-41.27(2)"a": 20% earned income deduction
        after_deduction = earned * (1 - p.earned_income_deduction.rate)

        # Per IAC 441-41.27(2)"c": 58% work incentive disregard (recipients only)
        is_recipient = spm_unit("is_tanf_enrolled", period)
        disregard = where(
            is_recipient,
            after_deduction * p.work_incentive_disregard.rate,
            0,
        )
        return max_(after_deduction - disregard, 0)
