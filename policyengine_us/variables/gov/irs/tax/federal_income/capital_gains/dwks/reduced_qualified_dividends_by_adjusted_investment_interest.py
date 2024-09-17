from policyengine_us.model_api import *


class reduced_qualified_dividends_by_adjusted_investment_interest(Variable):
    value_type = float
    entity = TaxUnit
    label = "IRS Form 1040 Schedule D worksheet (part 1 of 6)"  # DWKS06
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f1040.pdf",
        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf",
        "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf",
    )

    def formula(tax_unit, period, parameters):
        # Form 1040 line 3a
        qualified_dividends = add(
            tax_unit, period, ["qualified_dividend_income"]
        )  # dwks2
        # From 6251 line 2c
        investment_interest = tax_unit(
            "investment_income_form_4952", period
        )  # dwks3
        # dwks4 always assumed to be zero
        adjusted_investment_interest = max_(0, investment_interest)  # dwks5
        return max_(
            0, qualified_dividends - adjusted_investment_interest
        )  # dwks6
