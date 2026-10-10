from policyengine_us.model_api import *


class ma_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62/Section2",
        # c.62C s.6(a): each individual with Massachusetts gross income over
        # $8,000 files a return, so a dependent reports their own income.
        "https://malegislature.gov/Laws/GeneralLaws/PartI/TitleIX/Chapter62C/Section6",
    )
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # MA Form 1, Line 10: Total 5.0% income (lines 3-10).
        federal_gross_income = add(tax_unit, period, ["irs_gross_income"])
        # Add back lines 6/7 losses dropped by irs_gross_income.
        loss_adjustment = tax_unit("ma_gross_income_loss_adjustment", period)
        # Under M.G.L. c. 62 § 2(a)(1)(C), earned income from foreign sources
        # excluded under section 911 of the Code is added to MA gross income.
        # It is neither interest, dividends nor capital gains, so the Part B
        # residual taxes it under § 2(b)(2).
        foreign_earned_income = tax_unit(
            "ma_foreign_earned_income_exclusion_addback", period
        )
        # Exclude Social Security, state/local tax refunds, and contributory
        # public pensions.
        # Under M.G.L. c. 62 § 2(a)(2)(E), contributory pensions from the US,
        # Massachusetts, or reciprocal states are excluded from MA gross income.
        # Noncontributory or non-reciprocal public pensions are not exempt.
        # PolicyEngine treats taxable_public_pension_income as exempt public pensions.
        # c.62 s.2(a)(2) deducts these items from the filer's federal gross
        # income. Dependents' income is not in it (irs_gross_income excludes
        # it; they report it on their own return), so deduct only the head's
        # and spouse's amounts.
        social_security_in_agi = add(tax_unit, period, ["taxable_social_security"])
        salt_refund_income = tax_unit_non_dep_sum(
            "salt_refund_income", tax_unit, period
        )
        public_pension = tax_unit_non_dep_sum(
            "taxable_public_pension_income", tax_unit, period
        )
        deductions = social_security_in_agi + salt_refund_income + public_pension
        return max_(
            0,
            federal_gross_income + loss_adjustment + foreign_earned_income - deductions,
        )
