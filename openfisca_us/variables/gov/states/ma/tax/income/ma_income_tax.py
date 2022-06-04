from openfisca_us.model_api import *


class ma_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax"
    unit = USD
    documentation = "Massachusetts State income tax."
    definition_period = YEAR
    is_eligible = in_state("MA")
    reference = "https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download"

    def formula(tax_unit, period, parameters):
        tax = parameters(period).states.ma.tax.income
        person = tax_unit.members

        # 1 | FILING STATUS

        filing_status = tax_unit("filing_status", period)

        # 2 | EXEMPTIONS

        exemptions = tax_unit("ma_income_tax_exemptions", period)

        # 3 | INCOME

        (
            wages,
            pensions,
            interest,
            business_income,
            farm_income,
            unemployment_compensation,
            rental_income,
        ) = [add(tax_unit, period, [var]) for var in (
            "employment_income",
            "pension_income",
            "interest_income",
            "self_employment_income",
            "farm_income",
            "unemployment_compensation",
            "rental_income",
        )]
        interest = add(tax_unit, period, ["interest_income"]) # Assumed to have a location in Massachusetts
        interest = max_(0, interest - tax.exemptions.interest[filing_status])

        part_b_income = max_(
            0,
            wages
            + pensions
            + interest
            + business_income
            + farm_income
            + unemployment_compensation
            + rental_income
        )

        # 4 | DEDUCTIONS

        deductions = tax_unit("ma_income_tax_deductions", period)

        part_b_income -= total_deductions + total_exemptions

        dividends = add(tax_unit, period, ["dividend_income"])

        part_b_income += dividends # The tax form also includes interest from banks not located in Massachusetts, but we assume all interest is from banks with a presence in MA.

        part_b_tax = tax.rates.part_b * part_b_income

def ma_exemptions(tax_unit, period, tax):
    filing_status = tax_unit("filing_status", period)
    person = tax_unit.members

    personal_exemptions = tax.exemptions.personal[filing_status]

    count_dependents = tax_unit("tax_unit_dependents", period)
    dependent_exemption = tax.exemptions.dependent[filing_status] * count_dependents

    age = person("age", period)
    dependent = tax_unit("is_tax_unit_dependent", period)
    count_aged = tax_unit.sum(~dependent & (age >= tax.exemptions.aged.age))
    aged_exemption = tax.exemptions.aged.amount * count_aged

    blind = person("is_blind", period)
    count_blind = tax_unit.sum(~dependent & blind)
    blind_exemption = tax.exemptions.blind * count_blind

    itemizes = tax_unit("tax_unit_itemizes", period)
    federal_medical_expense_deduction = tax_unit("medical_expense_deduction", period)

    medical_dental_exemption = itemizes * federal_medical_expense_deduction

    adoption_exemption = 0 # Assumed to be zero

    return (
        personal_exemptions
        + dependent_exemption
        + aged_exemption
        + blind_exemption
        + medical_dental_exemption
        + adoption_exemption
    )