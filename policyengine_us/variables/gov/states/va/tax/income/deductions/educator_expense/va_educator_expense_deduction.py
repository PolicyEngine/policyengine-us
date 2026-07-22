from policyengine_us.model_api import *


class va_educator_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia eligible educator expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/vacode/title58.1/section58.1-322.03/",
        "https://www.tax.virginia.gov/sites/default/files/inline-files/2026-legislative-summary.pdf#page=10",
    )

    def formula(tax_unit, period, parameters):
        # Va. Code 58.1-322.03: the lesser of $500 or eligible educator expenses
        # (not claimed federally) per eligible educator. Available for TY2022-2024
        # and, reinstated by the 2026 Appropriation Act (HB 30), TY2026+; the cap
        # is 0 for TY2025 (and before TY2022), so the deduction is gated by year.
        cap = parameters(
            period
        ).gov.states.va.tax.income.deductions.educator_expense.cap
        person = tax_unit.members
        capped = min_(person("va_educator_expenses", period), cap)
        return tax_unit.sum(capped)
