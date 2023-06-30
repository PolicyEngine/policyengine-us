from policyengine_us.model_api import *

class la_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana itemized deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.louisiana.gov/TaxForms/IT540iWEB(2022)D1.pdf"
    defined_for = StateCode.LA

    def formula(tax_unit, period, parameters):
        medical_expenses = tax_unit("medical_expense_deduction", period)
        excess_itemized = max(medical_expenses - tax_unit("la_standard_deduction", period), 0)
        return excess_itemized
