from policyengine_us.model_api import *


class mn_k12_education_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota K-12 Education Expense Subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0132#stat.290.0132.9",
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1m-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mn.tax.income.subtractions.k12_education
        # Count K-12 children - simplified, using count without grade distinction
        # In practice, different limits apply for K-6 vs 7-12
        # Using average limit as approximation: (1625 + 2500) / 2 = 2062.50
        # For more accuracy, would need per-child grade tracking
        k12_children = tax_unit("mn_k12_qualifying_children", period)
        # Get qualifying expenses
        expenses = tax_unit("k12_tuition_and_fees", period)
        # Maximum subtraction - using 7-12 max as upper bound since we can't
        # distinguish grades
        max_subtraction = k12_children * p.cap.higher
        # Subtraction is lesser of expenses or maximum
        return min_(expenses, max_subtraction)
