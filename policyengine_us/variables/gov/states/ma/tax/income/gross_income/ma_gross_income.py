from policyengine_us.model_api import *


class ma_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2"
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # MA Form 1, Line 10: Total 5.0% income (lines 3-10).
        federal_gross_income = add(tax_unit, period, ["irs_gross_income"])
        # Add back lines 6/7 losses dropped by irs_gross_income.
        loss_adjustment = tax_unit("ma_gross_income_loss_adjustment", period)
        # Exclude foreign earned income, Social Security, state/local tax refunds,
        # and contributory public pensions.
        # Under M.G.L. c. 62 § 2(a)(2)(E), contributory pensions from the US,
        # Massachusetts, or reciprocal states are excluded from MA gross income.
        # Noncontributory or non-reciprocal public pensions are not exempt.
        # PolicyEngine treats taxable_public_pension_income as exempt public pensions.
        foreign_earned_income = tax_unit("foreign_earned_income_exclusion", period)
        social_security_in_agi = add(tax_unit, period, ["taxable_social_security"])
        salt_refund_income = add(tax_unit, period, ["salt_refund_income"])
        public_pension = add(tax_unit, period, ["taxable_public_pension_income"])
        deductions = (
            foreign_earned_income
            + social_security_in_agi
            + salt_refund_income
            + public_pension
        )
        return max_(0, federal_gross_income + loss_adjustment - deductions)
