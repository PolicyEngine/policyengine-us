from policyengine_us.model_api import *


class taxable_income_minus_gains(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 5 of 6)"  # DWKS14
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sd--2023.pdf#page=16",
    )

    def formula(tax_unit, period, parameters):
        # Schedule D Tax Worksheet line 1
        taxable_income = tax_unit("taxable_income", period)  #
        # Schedule D Tax Worksheet line 13
        computed_gains_after_1250_and_28_percent_rate_gains = tax_unit(
            "computed_gains_after_1250_and_28_percent_rate_gains", period
        )  # dwks13
        # Schedule D Tax Worksheet line 14
        return max_(
            0,
            taxable_income
            - computed_gains_after_1250_and_28_percent_rate_gains,
        ) * tax_unit("has_qdiv_or_ltcg", period)
