from openfisca_us.model_api import *


class ma_income_tax_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax exemptions"
    unit = USD
    definition_period = YEAR
    is_eligible = in_state("MA")
    reference = "https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download"

    def formula(tax_unit, period, parameters):
        tax = parameters(period).states.ma.tax.income
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