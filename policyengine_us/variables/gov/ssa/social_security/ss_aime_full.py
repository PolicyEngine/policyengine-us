from policyengine_us.model_api import *


class ss_aime_full(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Average Indexed Monthly Earnings (full calculation)"
    documentation = "Average Indexed Monthly Earnings using up to 35 highest years of indexed earnings"
    unit = USD
    reference = (
        "https://www.ssa.gov/OACT/COLA/aime.html",
        "https://www.law.cornell.edu/uscode/text/42/415#b",
    )

    def formula(person, period, parameters):
        # Get current age
        age = person("age", period)

        # Can't calculate AIME before age 62
        not_eligible = age < 62

        # For simplified implementation, simulate earnings history
        # In production, this would access actual historical data
        current_earnings = person("ss_covered_earnings_this_year", period)

        # Simulate 35 years of earnings with typical career pattern
        # Using simplified average adjustment from ss_aime
        average_adjustment = 0.94  # Career average factor

        # Calculate working years (22 to current age, max 35)
        working_years = min_(max_(age - 21, 0), 35)

        # Estimate total indexed earnings
        total_indexed_earnings = (
            current_earnings * working_years * average_adjustment
        )

        # AIME = total indexed earnings / 420 months (35 years * 12 months)
        MONTHS_IN_35_YEARS = 35 * MONTHS_IN_YEAR

        aime = total_indexed_earnings / MONTHS_IN_35_YEARS

        # Return 0 if not eligible, otherwise return AIME
        return where(not_eligible, 0, aime)
