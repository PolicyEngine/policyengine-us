from policyengine_us.model_api import *


class computed_gains_after_1250_and_28_percent_rate_gains(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 4 of 6)"  # DWKS13
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f1040.pdf",
        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf",
        "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf",
    )

    def formula(tax_unit, period, parameters):
        unrecaptured_section_1250_gain = add(
            tax_unit, period, ["unrecaptured_section_1250_gain"]
        )  # e24515
        # Sch D lines 18 and 19, respectively
        added_1250_and_28_percent_rate_gains = (
            unrecaptured_section_1250_gain
            + add(tax_unit, period, ["capital_gains_28_percent_rate_gain"])
        )  # dwks11
        adjusted_capital_gains_reduced_by_investment_income = tax_unit(
            "adjusted_capital_gains_reduced_by_investment_income", period
        )  # dwks09
        min_adjusted_gains_and_added_gains = min_(
            adjusted_capital_gains_reduced_by_investment_income,
            added_1250_and_28_percent_rate_gains,
        )  # dwks12
        computed_dividends_gains_whether_has_gains = tax_unit(
            "computed_dividends_gains_whether_has_gains", period
        )  # dwks10
        return (
            computed_dividends_gains_whether_has_gains
            - min_adjusted_gains_and_added_gains
        ) * tax_unit("has_qdiv_or_ltcg", period)
