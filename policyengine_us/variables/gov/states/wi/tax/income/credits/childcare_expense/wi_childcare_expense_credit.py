from policyengine_us.model_api import *


class wi_childcare_expense_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin childcare expense credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=2",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1-Inst.pdf#page=17",
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/07/9g",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wi.tax.income.credits
        wi_max_expense = p.childcare_expense.max_expense
        fraction = p.childcare_expense.fraction
        has_wi_expense_limit = wi_max_expense > 0
        # For 2024+, Wisconsin recomputes the credit using its own
        # higher expense limits ($10,000/$20,000) per 71.07(9g)(c)5.
        # For 2022-2023, it uses a fraction of the federal credit.
        federal_cdcc_potential = tax_unit("cdcc_potential", period)
        # Recompute with WI limits when applicable.
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        capped_eligible = tax_unit("capped_count_cdcc_eligible", period)
        wi_expense_cap = wi_max_expense * capped_eligible
        wi_capped_expenses = min_(expenses, wi_expense_cap)
        lower_earnings = tax_unit("min_head_spouse_earned", period)
        wi_relevant_expenses = min_(wi_capped_expenses, lower_earnings)
        cdcc_rate = tax_unit("cdcc_rate", period)
        wi_cdcc_potential = wi_relevant_expenses * cdcc_rate
        return where(
            has_wi_expense_limit,
            fraction * wi_cdcc_potential,
            fraction * federal_cdcc_potential,
        )
