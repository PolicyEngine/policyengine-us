from policyengine_us.model_api import *


class ar_tea_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas TEA countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/arkansas/208-00-13-Ark-Code-R-SS-001"
    defined_for = StateCode.AR

    def formula(spm_unit, period, parameters):
        # Per 208.00.13 Ark. Code R. Section 001, Section 3.3
        p = parameters(period).gov.states.ar.dhs.tea.income.work_deduction
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Step 1: Apply 20% work expense deduction (applies to all)
        after_work_expense = gross_earned * (1 - p.expense_rate)

        # Step 2: Apply 60% work incentive deduction (only for ongoing recipients)
        is_enrolled = spm_unit("is_tanf_enrolled", period)

        # For initial applicants: only 20% work expense deduction
        # For ongoing recipients: 20% work expense + 60% work incentive
        return where(
            is_enrolled,
            after_work_expense * (1 - p.incentive_rate),
            after_work_expense,
        )
