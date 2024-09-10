from policyengine_us.model_api import *


class reduced_qualified_dividends_by_adjusted_investment_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Reduced qualified dividends by adjusted investment interest"  # DWKS6
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f6251.pdf",
        "https://www.irs.gov/pub/irs-pdf/i6251.pdf",
    )

    def formula(tax_unit, period, parameters):
        qualified_dividends = add(
            tax_unit, period, ["qualified_dividend_income"]
        )  # dwks2 # Form 1040 line 3a
        investment_interest = tax_unit(
            "investment_income_form_4952", period
        )  # dwks3 # From 6251 line 2c
        # dwks4 always assumed to be zero
        adjusted_investment_interest = max_(0, investment_interest)  # dwks5
        return max_(
            0, qualified_dividends - adjusted_investment_interest
        )  # dwks6
