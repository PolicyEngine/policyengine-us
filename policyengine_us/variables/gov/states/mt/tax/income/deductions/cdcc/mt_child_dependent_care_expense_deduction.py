from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana child dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.standard.mt_child_dependent_care_expense_deduction
        agi = tax_unit("mt_agi", period)
        care_expenses = ("childcare_expenses", period)
        num_dependents = tax_unit("num_dependents", period)

        # Determine the number of qualifying children (under 15 or disabled)
        qualifying_child = num_dependents[(num_dependents <= p.threshold.age) | (num_dependents == "disabled")]

        income_qualifies = agi <= p.income_threshold[qualifying_child]
        

        return income_qualifies * min_(p.amount[qualifying_child], care_expenses)
