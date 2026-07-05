from policyengine_us.model_api import *


class wi_childcare_expense_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin childcare expense subtraction from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/43",
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB.pdf",
        "https://www.revenue.wi.gov/TaxForms2021/2021-ScheduleSB-inst.pdf#page=7",
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
        earnings_capped_expenses = min_(
            capped_expenses, tax_unit("min_head_spouse_earned", period)
        )
        # §71.05(6)(b)43.e.: a claimant is subject to the special rules in
        # IRC §21(e)(2) and (4), so a married claimant must file jointly
        # unless treated as unmarried.
        eligible = tax_unit("cdcc_filing_status_eligible", period)
        return eligible * earnings_capped_expenses
