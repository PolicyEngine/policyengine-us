from policyengine_us.model_api import *


class va_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia itemized medical expense deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2025-sch-a-instructions.pdf#page=1"

    def formula(tax_unit, period, parameters):
        return tax_unit("medical_expense_deduction", period)

    def formula_2024(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.deductions.itemized
        medical_expenses = add(tax_unit, period, ["itemized_medical_expenses"])
        federal_agi = max_(tax_unit("adjusted_gross_income", period), 0)
        return max_(medical_expenses - p.medical_expense_floor * federal_agi, 0)
