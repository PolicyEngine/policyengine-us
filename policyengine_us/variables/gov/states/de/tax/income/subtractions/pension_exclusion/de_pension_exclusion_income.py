from policyengine_us.model_api import *


class de_pension_exclusion_income(Variable):
    value_type = float
    entity = Person
    label = "Income sources for the Delaware pension exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    reference = "https://revenuefiles.delaware.gov/2025/PITForms_Instructions/Instructions/PIT-RES_Instructions_2025-01.pdf#page=6"

    def formula(person, period, parameters):
        # Per DE PIT-RES Line 6 instructions, the eligible-income basket for
        # the pension exclusion uses each source individually. Capital losses
        # are limited (they don't drown otherwise-eligible interest, dividends,
        # pension, and rental income), so floor capital_gains at zero before
        # adding it to the basket.
        return (
            person("dividend_income", period)
            + max_(0, person("capital_gains", period))
            + person("taxable_interest_income", period)
            + person("rental_income", period)
            + person("taxable_pension_income", period)
        )
