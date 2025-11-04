from policyengine_us.model_api import *


class pa_tanf_earned_income_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF earned income deductions"
    documentation = "Pennsylvania TANF applies a $90 initial work expense deduction, then disregards 50% of remaining earned income, then applies a $200 additional work expense deduction."
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code § 183.94"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf.income.deductions
        person = spm_unit.members

        # Use federal baseline (Person, MONTH) and aggregate to SPMUnit
        monthly_gross = spm_unit.sum(
            person("tanf_gross_earned_income", period)
        )

        # Step 1: Subtract $90 initial work expense deduction
        initial_deduction = p.initial_work_expense.amount
        after_initial = max_(monthly_gross - initial_deduction, 0)

        # Step 2: Apply 50% earned income disregard
        disregard_percentage = p.earned_income_disregard.percentage
        disregarded_amount = after_initial * disregard_percentage

        # Step 3: Add $200 additional work expense deduction
        additional_deduction = p.additional_work_expense.amount

        # Total monthly deduction
        return initial_deduction + disregarded_amount + additional_deduction
