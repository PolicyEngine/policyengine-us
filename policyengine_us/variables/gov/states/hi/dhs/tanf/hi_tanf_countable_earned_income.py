from policyengine_us.model_api import *


class hi_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/03/HAR-17-676-INCOME.pdf",
        "https://humanservices.hawaii.gov/wp-content/uploads/2024/12/Hawaii_TANF_State_Plan_Signed_Certified-Eff_20231001.pdf",
    )
    defined_for = StateCode.HI

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.hi.dhs.tanf.income.deductions

        # Start with gross earned income (federal baseline)
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Step 1: Apply 20% standard deduction
        after_standard = gross_earned * (1 - p.standard.rate)

        # Step 2: Apply $200 flat rate deduction
        after_flat = max_(after_standard - p.flat_rate.amount, 0)

        # Step 3: Apply 55% earned income disregard
        # NOTE: 55% applies for months 1-24; 36% applies after month 24
        # PolicyEngine cannot track months of receipt, so 55% is used as default
        countable_earned = after_flat * (1 - p.earned_income_disregard.rate)

        return max_(countable_earned, 0)
