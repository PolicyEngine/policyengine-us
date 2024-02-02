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
        ).gov.states.id.tax.income.deductions.dependent_care_expenses.cap
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        # In 2023 Idaho implemented an increased cap independent of the number of children
        if p.available:
            amount_per_child = p.amount
        else:
            capped_count_cdcc_eligible = tax_unit(
                "capped_count_cdcc_eligible", period
            )
            cdcc = parameters(period).gov.irs.credits.cdcc
            amount_per_child = cdcc.max * capped_count_cdcc_eligible
        eligible_capped_expenses = min_(expenses, amount_per_child)
        # cap further to the lowest earnings between the taxpayer and spouse
        return min_(
            eligible_capped_expenses,
            tax_unit("min_head_spouse_earned", period),
        )
