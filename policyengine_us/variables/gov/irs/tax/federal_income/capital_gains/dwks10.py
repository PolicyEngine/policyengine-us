from policyengine_us.model_api import *


class dwks10(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 3 of 6)"
    unit = USD

    def formula(tax_unit, period, parameters):
        dwks10_if_gains = add(tax_unit, period, ["dwks06", "dwks09"])
        dwks10_if_no_gains = max_(
            0,
            min_(
                add(
                    tax_unit,
                    period,
                    ["long_term_capital_gains", "qualified_dividend_income"],
                ),
                tax_unit("net_capital_gains", period),
            ),
        ) + add(tax_unit, period, ["non_sch_d_capital_gains"])
        return where(
            tax_unit("has_qdiv_or_ltcg", period),
            dwks10_if_gains,
            dwks10_if_no_gains,
        )
