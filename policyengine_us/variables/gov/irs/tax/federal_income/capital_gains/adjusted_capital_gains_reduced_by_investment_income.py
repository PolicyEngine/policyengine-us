from policyengine_us.model_api import *


class adjusted_capital_gains_reduced_by_investment_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted capital gains reduced by investment income"  # DWKS9
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
        net_capital_gains = tax_unit("net_capital_gains", period)  # c23650
        capped_net_capital_gains = min_(
            total_cap_gains_and_dividends, net_capital_gains
        )  # dwks7 # SchD lines 15 and 16, respectively
        # dwks8 = min(dwks3, dwks4)
        # adjusted_capital_gains_reduced_by_investment_income = max(0., capped_net_capital_gains - dwks8)
        # BELOW TWO STATEMENTS ARE UNCLEAR IN LIGHT OF adjusted_capital_gains_reduced_by_investment_income=... COMMENT
        non_sch_d_capital_gains = add(
            tax_unit, period, ["non_sch_d_capital_gains"]
        )  # e01100
        cpaital_gains_adjusted_for_non_sch_d_gains = where(
            non_sch_d_capital_gains > 0,
            non_sch_d_capital_gains,
            max_(0, capped_net_capital_gains) + non_sch_d_capital_gains,
        )  # c24510
        return max_(
            0,
            cpaital_gains_adjusted_for_non_sch_d_gains
            - min_(0, tax_unit("investment_income_form_4952", period)),
        )
