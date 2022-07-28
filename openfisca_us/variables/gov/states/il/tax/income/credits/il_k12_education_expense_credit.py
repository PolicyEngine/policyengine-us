from openfisca_us.model_api import *

class il_k12_education_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "IL K-12 Education Expense Credit"
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        tuition_and_fees = tax_unit("tuition_and_fees", period) - 250
        return min(750, max(0, tuition_and_fees) * 0.25)