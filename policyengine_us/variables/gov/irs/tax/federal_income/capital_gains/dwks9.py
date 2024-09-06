from policyengine_us.model_api import *


class dwks9(Variable):
    value_type = float
    entity = TaxUnit
    label = "DWKS9"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f6251.pdf",
        "https://www.irs.gov/pub/irs-pdf/i6251.pdf",
        "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf",
    )

    def formula(tax_unit, period, parameters):
        total_cap_gains_and_dividends = add(
            tax_unit,
            period,
            ["long_term_capital_gains", "qualified_dividend_income"],
        )  # p23250
        c23650 = tax_unit("c23650", period)
        dwks7 = min_(
            total_cap_gains_and_dividends, c23650
        )  # SchD lines 15 and 16, respectively
        # dwks8 = min(dwks3, dwks4)
        # dwks9 = max(0., dwks7 - dwks8)
        # BELOW TWO STATEMENTS ARE UNCLEAR IN LIGHT OF dwks9=... COMMENT
        non_sch_d_capital_gains = add(
            tax_unit, period, ["non_sch_d_capital_gains"]
        )  # e01100
        c24510 = where(
            non_sch_d_capital_gains > 0,
            non_sch_d_capital_gains,
            max_(0, dwks7) + non_sch_d_capital_gains,
        )
        return max_(
            0,
            c24510 - min_(0, tax_unit("investment_income_form_4952", period)),
        )
