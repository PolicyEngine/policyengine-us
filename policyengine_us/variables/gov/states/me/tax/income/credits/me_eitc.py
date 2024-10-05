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
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.me.tax.income.credits.eitc
        match_rate = where(
            tax_unit("eitc_child_count", period) > 0,
            p.rate.with_qualifying_child,
            p.rate.no_qualifying_child,
        )
        return federal_eitc * match_rate
