from policyengine_us.model_api import *


class me_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mainelegislature.org/legis/statutes/36/title36sec5219-S.html"
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # 36 M.R.S. § 5219-S(5)-(6): childless filers aged 18-24 who fail the
        # federal EITC only on the minimum-age floor are treated as eligible,
        # with the credit computed as if they qualified federally. Take the
        # larger of the actual federal EITC and the pro forma amount for that
        # cohort; the pro forma is zero for tax units outside the expansion.
        federal_eitc = max_(
            tax_unit("eitc", period),
            tax_unit("me_pro_forma_childless_eitc", period),
        )
        p = parameters(period).gov.states.me.tax.income.credits.eitc
        match_rate = where(
            tax_unit("eitc_child_count", period) > 0,
            p.rate.with_qualifying_child,
            p.rate.no_qualifying_child,
        )
        return federal_eitc * match_rate
