from policyengine_us.model_api import *


class me_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "ME EITC"
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
        person = tax_unit.members
        is_qualifying_child = person("is_eitc_qualifying_child", period)
        has_qualifying_child = tax_unit.sum(is_qualifying_child) > 0
        percentage = where(
            has_qualifying_child,
            p.percent_with_qualifying_child,
            p.percent_without_qualifying_child,
        )

        # Return the net Maine EITC.
        return eitc * percentage
