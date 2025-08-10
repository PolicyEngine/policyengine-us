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
        # Simplified AIME calculation for initial implementation
        # TODO: Implement full 35-year earnings history tracking
        # TODO: Implement wage indexing
        # TODO: Select highest 35 years

        # For now, just use current year earnings as a proxy
        current_earnings = person("ss_covered_earnings_this_year", period)

        # AIME is based on 35 years of earnings divided by 420 months
        # For this simplified version, we'll assume only current year earnings
        # Real implementation needs historical earnings tracking

        # If person has earnings, calculate simplified AIME
        # This is just for making initial tests pass
        MONTHS_IN_35_YEARS = 420

        return current_earnings / MONTHS_IN_35_YEARS

