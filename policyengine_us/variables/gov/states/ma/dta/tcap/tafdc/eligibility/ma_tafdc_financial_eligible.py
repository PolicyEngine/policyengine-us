from policyengine_us.model_api import *


class ma_tafdc_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) due to income"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-000"
    )
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        # old code below
        # income = add(
        #    spm_unit,
        #    period,
        #    [
        #        "ma_tafdc_partially_disregarded_earned_income", # <-- this variable gives 50% disregard, contradict to the application rule.
        #        "ma_tcap_unearned_income",
        #    ],
        # )

        # The code below align with the application rule, no 50% disregard for earned income
        gross_earned_income = add(
            spm_unit, period, ["ma_tcap_gross_earned_income"]
        )
        deductions = add(
            spm_unit,
            period,
            [
                "ma_tafdc_work_related_expense_deduction",
                "ma_tafdc_dependent_care_deduction",
            ],
        )
        countable_unearned_income = spm_unit(
            "ma_tafdc_countable_unearned_income", period
        )

        total_monthly_countable_income = max_(
            gross_earned_income - deductions + countable_unearned_income, 0
        )  # Maybe create a new variable for this total_countable_income at a spm unit level, can be used in "full_earned_income_disregard_eligible"
            # Can be used in "ma_tafdc_full_earned_income_disregard_eligible"
        payment_standard = spm_unit("ma_tafdc_payment_standard", period)

        return total_monthly_countable_income < payment_standard
