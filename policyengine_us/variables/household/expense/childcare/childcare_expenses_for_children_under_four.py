from policyengine_us.model_api import *


class childcare_expenses_for_children_under_four(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare expenses for children under age four"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # For now define this as total childcare expenses
        # times the share of children in the tax unit under the age of four.
        children = tax_unit("tax_unit_children", period)
        person = tax_unit.members
        child_under_four = person("age", period) < 4
        children_under_four = tax_unit.sum(child_under_four)
        tax_unit_childcare_expenses = tax_unit(
            "tax_unit_childcare_expenses", period
        )
        return children_under_four * tax_unit_childcare_expenses / children
