from policyengine_us.model_api import *


class id_household_and_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho household and dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.dependent_care_expenses
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        # In 2023 Idaho implemented an increased cap independent of the number of children
        limit = max_(tax_unit("id_cdcc_limit", period), p.cap)
        eligible_capped_expenses = min_(expenses, limit)
        # cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
