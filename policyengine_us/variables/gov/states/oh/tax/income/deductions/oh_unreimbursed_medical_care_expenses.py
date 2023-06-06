from policyengine_us.model_api import *


class oh_unreimbursed_medical_care_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Unreimbursed Medical and Health Care Expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        premiums_expenses = sum(person("health_insurance_premiums", period))
        medical_expenses = sum(
            person("medical_out_of_pocket_expenses", period)
        )  # moop
        federal_agi = tax_unit("adjusted_gross_income", period)

        rate = parameters(
            period
        ).gov.states.oh.tax.income.deductions.unreimbursed_medical_care_expenses.rate
        adjusted_moop = max(0, medical_expenses - rate * federal_agi)
        
        return adjusted_moop + premiums_expenses
