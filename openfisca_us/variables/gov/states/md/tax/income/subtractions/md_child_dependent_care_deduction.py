from openfisca_us.model_api import *


class md_child_dependent_care_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Child and Dependent Care Expenses"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # You may subtract the cost of caring for your dependents while you work. There is a limitation of $3,000 ($6,000 if two or more dependents receive care). Enter on line 9 the smaller of (a) the amount on line 6 of federal Form 2441 or (b) $3,000 ($6,000 if two or more dependents receive care). You may also be entitled to credits fo r these taxable expenses. See instructions for Part B and Part CC of Form 502CR.
        expenses = tax_unit("cdcc_relevant_expenses", period)

        count_cdcc_eligible = tax_unit("count_cdcc_eligible", period)
        max_per_child = parameters(
            period
        ).gov.states.md.tax.income.subtractions.child_dependent_care_deduction.max
        max_dependents = parameters(
            period
        ).gov.states.md.tax.income.subtractions.child_dependent_care_deduction.max_dependents
        max_possible_expenses = max_per_child * count_cdcc_eligible

        # Return the smaller of max_possible_expenses and expenses.
        return min_(max_possible_expenses, expenses)
