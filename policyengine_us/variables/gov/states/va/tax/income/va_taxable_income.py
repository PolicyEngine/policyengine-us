from policyengine_us.model_api import *


class va_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
        "https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2022/760-2022.pdf#page=1"
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        agi = tax_unit("va_agi", period)
        ded = tax_unit("va_deductions", period)
        exemptions = tax_unit("va_total_exemptions", period)
        total_deductions = ded + exemptions
        # Virginia allows a deduction (atop itemized deductions) for the
        # relevant expenses for the federal Child and Dependent Care Credit.
        cdcc_expense_deduction = tax_unit(
            "va_child_dependent_care_expense_deduction", period
        )
        return max_(agi - total_deductions - cdcc_expense_deduction, 0)
