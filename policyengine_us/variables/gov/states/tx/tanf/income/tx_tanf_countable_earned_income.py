from policyengine_us.model_api import *


class tx_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1340-income-limits",
        "https://www.law.cornell.edu/regulations/texas/1-TAC-372-605",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        person_earned = person("tx_tanf_gross_earned_income", period)
        p = parameters(period).gov.states.tx.tanf.income

        work_expense_deduction = min_(p.work_expense_deduction, person_earned)
        earned_after_work_expense = max_(
            person_earned - work_expense_deduction, 0
        )

        disregard_rate = p.earned_income_disregard_rate
        disregard_cap = p.earned_income_disregard_cap

        potential_disregard = earned_after_work_expense * disregard_rate
        actual_disregard = min_(potential_disregard, disregard_cap)

        countable_person_earned = max_(
            earned_after_work_expense - actual_disregard, 0
        )

        return spm_unit.sum(countable_person_earned)
