from policyengine_us.model_api import *


class mn_k12_education_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota K-12 Education Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0674",
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1ed-25.pdf",
    )
    defined_for = "mn_k12_education_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.k12_education
        # Count qualifying K-12 children
        k12_children = tax_unit("mn_k12_qualifying_children", period)
        # Get qualifying expenses
        expenses = tax_unit("k12_tuition_and_fees", period)
        # Line 11: expenses * 75%
        expense_credit = expenses * p.expense_rate
        # Line 12: Calculate credit limit based on income
        base_credit_limit = k12_children * p.amount_per_child
        # Phase-out if AGI exceeds threshold
        agi = tax_unit("adjusted_gross_income", period)
        excess_income = max_(0, agi - p.income_threshold)
        # Use different phase-out rate for 1 child vs multiple
        phaseout_rate = where(
            k12_children == 1,
            p.phaseout_rate_one_child,
            p.phaseout_rate_multiple_children,
        )
        phaseout_amount = excess_income * phaseout_rate
        credit_limit = max_(0, base_credit_limit - phaseout_amount)
        # Credit is lesser of expense credit or credit limit
        return min_(expense_credit, credit_limit)
