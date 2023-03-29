from policyengine_us.model_api import *


class me_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5219-S.html"
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # First get their federal EITC.
        eitc = tax_unit("earned_income_tax_credit", period)

        # Then get the ME EITC part of the parameter tree.
        p = parameters(period).gov.states.me.tax.income.credits.eitc

        # Determine applicable percentage of federal EITC.
        # Depends on whether or not they have at least one qualifying child.
        percentage = where(
            tax_unit("eitc_child_count", period) > 0,
            p.rate.with_qualifying_child,
            p.rate.no_qualifying_child,
        )

        # Return the net Maine EITC.
        return eitc * percentage
