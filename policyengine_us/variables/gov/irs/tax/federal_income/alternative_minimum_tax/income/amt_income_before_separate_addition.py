from policyengine_us.model_api import *


class amt_income_before_separate_addition(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income before the married filing separately addition"
    unit = USD
    documentation = (
        "Alternative minimum taxable income determined without the increase "
        "26 U.S.C. 55(d)(2) makes for a married individual filing a separate "
        "return, which is figured on this amount (Form 6251 line 4 before the "
        "additional amount)."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/55#d_2",
        "https://www.law.cornell.edu/uscode/text/26/56",
        # Form 6251 line 1 keeps a negative amount when taxable income is zero
        "https://www.irs.gov/pub/irs-prior/f6251--2024.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/f6251--2025.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/i6251--2025.pdf#page=2",
        # 2017 Form 6251 lines 6 and 7, and their instructions.
        "https://www.irs.gov/pub/irs-prior/f6251--2017.pdf#page=1",
        # PDF pages 2-3
        "https://www.irs.gov/pub/irs-prior/i6251--2017.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.income.amt
        # Form 6251 line 1: Form 1040 line 15 if more than zero. If line 15
        # is zero, line 11 minus line 14, entered as a negative amount if
        # less than zero. Before 2018 the personal exemptions were not
        # subtracted, which taxable income plus exemptions also gives.
        taxable_income = tax_unit("taxable_income", period)
        exemptions = tax_unit("exemptions", period)
        agi = tax_unit("adjusted_gross_income", period)
        deductions = tax_unit("taxable_income_deductions", period)
        # From 2018 both branches equal agi - deductions; the taxable income
        # branch only differs before 2018, when exemptions were subtracted.
        line_1 = where(
            taxable_income > 0,
            taxable_income + exemptions,
            agi - deductions,
        )
        # 2025 line 1a: deductions in line 14 that are not taken for the AMT.
        deductions_add_back = (
            add(tax_unit, period, p.deductions_add_back) if p.deductions_add_back else 0
        )
        # 2025 line 2b (2017 line 7): refunds of state and local taxes in
        # income are not AMTI (26 U.S.C. 56(b)(1)(C), formerly (D)). Subtract
        # what irs_gross_income put in AGI: each head's or spouse's refund,
        # floored at zero. Dependents' refunds are on their own returns.
        person = tax_unit.members
        filer = ~person("is_tax_unit_dependent", period)
        tax_refunds = tax_unit.sum(
            filer * max_(0, person("salt_refund_income", period))
        )
        # Section 68 does not apply to AMTI (26 U.S.C. 56(b)(1)(E), formerly
        # (F)), so the itemized deduction reduction in line 1 comes back out
        # (2017 line 6).
        section_68_reduction = where(
            tax_unit("tax_unit_itemizes", period),
            tax_unit("itemized_taxable_income_deductions_reduction", period),
            0,
        )
        return (
            line_1
            + deductions_add_back
            + tax_unit("amt_excluded_deductions", period)
            - tax_refunds
            - section_68_reduction
        )
