from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana child dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = "mt_child_dependent_care_expense_deduction_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.standard.mt_child_dependent_care_expense_deduction
        agi = tax_unit("mt_agi", period)
        care_expenses = ("childcare_expenses", period)
        num_dependents = tax_unit("num_dependents", period)

        qualifying_child = num_dependents[(num_dependents <= p.threshold.age) | (num_dependents == "disabled")]

        return min(p.amount[qualifying_child], care_expense)
