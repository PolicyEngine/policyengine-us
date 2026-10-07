from policyengine_us.model_api import *


class amt_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/56",
        # Form 6251 line 1 keeps a negative amount when taxable income is zero
        "https://www.irs.gov/pub/irs-prior/f6251--2024.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/f6251--2025.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/i6251--2025.pdf#page=2",
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
        line_1 = where(
            taxable_income > 0,
            taxable_income + exemptions,
            agi - deductions,
        )
        # 2025 line 1a: deductions in line 14 that are not taken for the AMT.
        deductions_add_back = (
            add(tax_unit, period, p.deductions_add_back) if p.deductions_add_back else 0
        )
        return (
            line_1
            + deductions_add_back
            + add(
                tax_unit,
                period,
                ["amt_excluded_deductions", "amt_separate_addition"],
            )
        )
