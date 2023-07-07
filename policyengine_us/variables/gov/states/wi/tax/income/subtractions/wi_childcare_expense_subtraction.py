from policyengine_us.model_api import *


class wi_childcare_expense_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin childcare expense subtraction from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdf"
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=7"
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        subtraction = parameters(period).gov.states.wi.tax.income.subtractions
        uncapped_expenses = tax_unit("tax_unit_childcare_expenses", period)
        eligible_dependents = tax_unit("count_cdcc_eligible", period)
        count_eligible = min_(
            eligible_dependents, subtraction.childcare_expense.max_dependents
        )
        capped_expenses = min_(
            uncapped_expenses,
            count_eligible * subtraction.childcare_expense.max_amount,
        )
        return min_(
            capped_expenses, tax_unit("min_head_spouse_earned", period)
        )
