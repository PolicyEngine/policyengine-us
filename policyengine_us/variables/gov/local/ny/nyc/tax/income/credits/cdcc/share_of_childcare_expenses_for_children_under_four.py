from policyengine_us.model_api import *


class share_of_childcare_expenses_for_children_under_four(Variable):
    value_type = float
    entity = TaxUnit
    label = "Share of Childcare expenses for children under age four"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Get the total expenses for children under age four.
        # Line 23 on Form IT-216.
        childcare_expenses_for_children_under_four = tax_unit(
            "childcare_expenses_for_children_under_four", period
        )

        # Get the total childcare expenses
        # Line 3a on Form IT-216.
        tax_unit_childcare_expenses = tax_unit("tax_unit_childcare_expenses", period)

        # Return the share of childcare expenses for children under age four
        return childcare_expenses_for_children_under_four / tax_unit_childcare_expenses
