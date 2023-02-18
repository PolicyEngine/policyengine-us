from policyengine_us.model_api import *


class nyc_cdcc_age_restricted_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare expenses for children under age four"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # For now define this as total childcare expenses
        # times the share of children in the tax unit under the age of four.

        # Get the CDCC parameter tree.
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.cdcc

        children = tax_unit("tax_unit_children", period)
        person = tax_unit.members
        qualifying_children = (
            person("age", period) < p.child_age_restriction
        )
        children_under_four = tax_unit.sum(qualifying_children)
        tax_unit_childcare_expenses = tax_unit(
            "tax_unit_childcare_expenses", period
        )
        return children_under_four * tax_unit_childcare_expenses / children
