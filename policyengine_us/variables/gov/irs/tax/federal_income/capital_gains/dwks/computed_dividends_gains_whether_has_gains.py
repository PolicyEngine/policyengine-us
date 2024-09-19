from policyengine_us.model_api import *


class computed_dividends_gains_whether_has_gains(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 3 of 6)"  # DWKS10
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sd--2023.pdf#page=16",
    )

    def formula(tax_unit, period, parameters):
        # Schedule D Tax Worksheet line 10
        if_gains = add(
            tax_unit,
            period,
            [
                "reduced_qualified_dividends_by_adjusted_investment_interest",
                "adjusted_capital_gains_reduced_by_investment_income",
            ],
        )  # dwks6 & 9
        if_no_gains = max_(
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
            if_gains,
            if_no_gains,
        )
