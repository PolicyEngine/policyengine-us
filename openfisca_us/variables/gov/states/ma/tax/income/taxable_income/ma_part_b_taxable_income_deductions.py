from openfisca_us.model_api import *


class ma_part_b_taxable_income_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part B taxable income deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-3"

    def formula(tax_unit, period, parameters):
        tax = parameters(period).states.ma.tax.income
        filing_status = tax_unit("filing_status", period)

        fica = tax_unit("employee_payroll_tax", period)
        fica = min_(
            tax.deductions.public_retirement_contributions,
            fica,
        )
        interest_and_dividends = add(
            tax_unit, period, ["interest_income", "dividend_income"]
        )

        interest_and_dividends = min_(
            tax.exemptions.interest[filing_status],
            interest_and_dividends,
        )

        rent = add(tax_unit, period, ["rent"])
        rent_deduction = tax.deductions.rent.share * rent
        rent_deduction = min_(
            rent_deduction,
            tax.deductions.rent.cap[filing_status],
        )

        personal_exemptions = tax.exemptions.personal[filing_status]
        person = tax_unit.members

        count_dependents = tax_unit("tax_unit_dependents", period)
        dependent_exemption = tax.exemptions.dependent * count_dependents

        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        count_aged = tax_unit.sum(
            ~dependent & (age >= tax.exemptions.aged.age)
        )
        aged_exemption = tax.exemptions.aged.amount * count_aged

        blind = person("is_blind", period)
        count_blind = tax_unit.sum(~dependent & blind)
        blind_exemption = tax.exemptions.blind * count_blind

        itemizes = tax_unit("tax_unit_itemizes", period)
        federal_medical_expense_deduction = tax_unit(
            "medical_expense_deduction", period
        )

        medical_dental_exemption = itemizes * federal_medical_expense_deduction

        adoption_exemption = 0  # Assumed to be zero

        return (
            fica
            + interest_and_dividends
            + rent_deduction
            + personal_exemptions
            + dependent_exemption
            + aged_exemption
            + blind_exemption
            + medical_dental_exemption
            + adoption_exemption
        )
