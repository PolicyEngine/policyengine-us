from openfisca_us.model_api import *


class state_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "State income tax medical expense deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        federal_deduction = tax_unit("medical_expense_deduction", period)
        itemizes = tax_unit("tax_unit_itemizes", period)
        state = tax_unit.household("state_code_str", period)
        is_allowed = parameters(period).states.tax.income.deductions.medical_expense.allowed
        return (is_allowed[state] & itemizes) * federal_deduction
