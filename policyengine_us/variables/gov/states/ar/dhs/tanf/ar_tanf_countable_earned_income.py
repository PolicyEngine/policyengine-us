from policyengine_us.model_api import *


class ar_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        # Per 208.00.13 Ark. Code R. Section 001, Section 3.3
        p = parameters(period).gov.states.ar.dhs.tanf.income.deductions
        gross_earned = spm_unit("tanf_gross_earned_income", period)

        # Step 1: Apply 20% work expense deduction
        after_work_expense = gross_earned * (1 - p.work_expense.rate)

        # Step 2: Apply 60% work incentive deduction
        countable_earned = after_work_expense * (1 - p.work_incentive.rate)

        return max_(countable_earned, 0)
