from openfisca_us.model_api import *


class ma_income_tax_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax deductions"
    unit = USD
    definition_period = YEAR
    is_eligible = in_state("MA")
    reference = "https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download"

    def formula(tax_unit, period, parameters):
        tax = parameters(period).states.ma.tax.income
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members

        public_retirement_contributions = person("employee_payroll_tax", period)
        capped_pension_contributions = min_(public_retirement_contributions, tax.deductions.public_retirement_contributions)

        rent = add(tax_unit, period, ["rent"])
        rent_deduction = tax.deductions.rent.share * rent
        capped_rent_deduction = min_(
            rent_deduction,
            tax.deductions.rent.cap[filing_status],
        )

        return capped_pension_contributions + capped_rent_deduction