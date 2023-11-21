from policyengine_us.model_api import *


class mt_child_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana child dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2022/12/2441-M_2022.pdf#page=1"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.deductions.standard.child_dependent_care_expense
        agi = tax_unit("mt_agi", period)
        care_expenses = tax_unit("tax_unit_childcare_expenses", period)
        reduction = p.reduction.calc(agi)
        reduced_expenses = max_(0, care_expenses - reduction)
        eligible_children = tax_unit(
            "mt_child_dependent_care_expense_deduction_eligible_children",
            period,
        )
        max_deduction = p.amount.calc(eligible_children)
        return min_(max_deduction, reduced_expenses)
