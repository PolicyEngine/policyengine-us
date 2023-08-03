from policyengine_us.model_api import *


class dwks9(Variable):
    value_type = float
    entity = TaxUnit
    label = "DWKS9"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p23250 = add(
            tax_unit,
            period,
            ["long_term_capital_gains", "qualified_dividend_income"],
        )
        c23650 = tax_unit("c23650", period)
        dwks7 = min_(p23250, c23650)  # SchD lines 15 and 16, respectively
        # dwks8 = min(dwks3, dwks4)
        # dwks9 = max(0., dwks7 - dwks8)
        # BELOW TWO STATEMENTS ARE UNCLEAR IN LIGHT OF dwks9=... COMMENT
        e01100 = add(tax_unit, period, ["non_sch_d_capital_gains"])
        c24510 = where(e01100 > 0, e01100, max_(0, dwks7) + e01100)
        return max_(
            0,
            c24510 - min_(0, tax_unit("investment_income_form_4952", period)),
        )
