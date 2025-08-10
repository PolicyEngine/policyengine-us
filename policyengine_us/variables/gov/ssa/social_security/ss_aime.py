from policyengine_us.model_api import *


class ss_aime(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Average Indexed Monthly Earnings (AIME)"
    documentation = "Average Indexed Monthly Earnings for Social Security benefit calculation"
    unit = USD
    reference = (
        "https://www.ssa.gov/OACT/COLA/aime.html",
        "https://www.law.cornell.edu/uscode/text/42/415#b",
    )

    def formula(person, period, parameters):
        # Check if we should use the full calculation
        age = person("age", period)

        # For demonstration: simulate 35 years of earnings
        # In production, this would access actual historical data
        current_earnings = person("ss_covered_earnings_this_year", period)

        # Simplified approach: assume constant real earnings over career
        # Adjust for typical career earnings pattern
        not_working_age = age < 22

        # Calculate years of potential earnings
        working_years = min_(age - 21, 35)
        no_working_years = working_years <= 0

        # For demonstration: assume current earnings represent mid-career level
        # Apply a simple career earnings curve
        # Use vectorized calculation for career earnings

        # Simplified career curve calculation
        # Average adjustment factor across career stages
        # Early career (30%): average of 0.5 to 1.0 = 0.75
        # Mid career (40%): 1.0
        # Late career (30%): average of 1.0 to 1.1 = 1.05
        # Weighted average: 0.3*0.75 + 0.4*1.0 + 0.3*1.05 = 0.94
        average_adjustment = 0.94

        total_indexed_earnings = (
            current_earnings * working_years * average_adjustment
        )

        # AIME = total indexed earnings / 420 months
        MONTHS_IN_35_YEARS = 420

        aime = total_indexed_earnings / MONTHS_IN_35_YEARS

        # Return 0 if not working age or no working years
        return where(not_working_age | no_working_years, 0, aime)
