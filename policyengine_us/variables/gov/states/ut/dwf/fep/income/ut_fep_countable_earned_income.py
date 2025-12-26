from policyengine_us.model_api import *


class ut_fep_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Utah TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-200-239"
    defined_for = StateCode.UT

    def formula(spm_unit, period, parameters):
        # Utah earned income after deductions per R986-200-239:
        # 1. Work expense allowance: $100 per employed person
        # 2. 50% earned income disregard on remaining earned income
        p = parameters(period).gov.states.ut.dwf.fep.income.deductions
        after_work_expense = add(
            spm_unit, period, ["ut_fep_earned_income_after_work_expense"]
        )
        # Countable = remainder * (1 - disregard_rate) = remainder * 0.5
        return after_work_expense * (1 - p.earned_income_disregard.rate)
