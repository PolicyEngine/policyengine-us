from openfisca_us.model_api import *


class dwks10(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "DWKS10"
    documentation = (
        "search taxcalc/calcfunctions.py for how calculated and used"
    )
    unit = USD

    def formula(tax_unit, period, parameters):
        dwks10_if_gains = add(tax_unit, period, ["dwks6", "dwks9"])
        dwks10_if_no_gains = max_(
            0,
            min_(
                add(
                    tax_unit,
                    period,
                    ["long_term_capital_gains", "qualified_dividend_income"],
                ),
                tax_unit("c23650", period),
            ),
        ) + add(tax_unit, period, ["non_sch_d_capital_gains"])
        return where(
            tax_unit("hasqdivltcg", period),
            dwks10_if_gains,
            dwks10_if_no_gains,
        )
