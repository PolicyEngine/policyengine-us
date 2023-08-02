from policyengine_us.model_api import *


class nyc_cdcc_share_qualifying_childcare_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Share of Childcare expenses that qualify towards NYC CDCC"
    unit = USD
    definition_period = YEAR
    unit = "/1"
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # Get the total expenses for children that qualify towards the NYC CDCC.
        # Line 23 on Form IT-216.
        childcare_expenses_for_children_under_four = tax_unit(
            "nyc_cdcc_age_restricted_expenses", period
        )
        # Get the total childcare expenses.
        # Line 3a on Form IT-216.
        tax_unit_childcare_expenses = tax_unit(
            "tax_unit_childcare_expenses", period
        )
        # Return the share of childcare expenses for children under age four
        # avoiding array divide-by-zero warning by not using where() function
        share = np.zeros_like(tax_unit_childcare_expenses)
        mask = tax_unit_childcare_expenses > 0
        share[mask] = (
            childcare_expenses_for_children_under_four[mask]
            / tax_unit_childcare_expenses[mask]
        )
        return share
