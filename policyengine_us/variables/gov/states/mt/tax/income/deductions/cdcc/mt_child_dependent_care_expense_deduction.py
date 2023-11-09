from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana child dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.standard.child_dependent_care_expense_deduction
        agi = tax_unit("mt_agi", period)
        care_expenses = tax_unit("tax_unit_childcare_expenses", period)
        reduced_expense = max_(0, care_expenses - p.threshold.income.calc(agi))
        eligible_children = tax_unit(
            "mt_child_dependent_care_expense_deduction_eligible_children",
            period,
        )
        return min_(p.amount.calc(eligible_children), reduced_expense)
