from policyengine_us.model_api import *


class ss_indexed_earnings(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security indexed earnings"
    documentation = "Annual earnings indexed to age 60 for Social Security benefit calculation"
    unit = USD
    reference = (
        "https://www.ssa.gov/OACT/ProgData/retirebenefit1.html",
        "https://www.law.cornell.edu/uscode/text/42/415#b_1",
    )

    def formula(person, period, parameters):
        # Get current age
        age = person("age", period)

        # Get covered earnings for this year
        covered_earnings = person("ss_covered_earnings_this_year", period)

        # If person is under 60, no indexing yet (will be indexed in future)
        # If person is 60 or over, index past earnings to age 60

        if age < 60:
            # Earnings not yet indexed
            return covered_earnings

        # For age 60+, we need to index this year's earnings
        # based on when it was earned relative to age 60

        # Calculate the year person turned 60
        birth_year = period.start.year - age
        year_turned_60 = birth_year + 60

        # Get wage indices
        p = parameters(period).gov.ssa

        # Earnings at age 60 and later are not indexed
        if period.start.year >= year_turned_60:
            return covered_earnings

        # Index earlier earnings to age 60
        wage_index_current = p.national_average_wage_index
        wage_index_at_59 = p.national_average_wage_index(
            f"{year_turned_60 - 1}-01-01"
        )

        # Index factor = wage index at age 59 / wage index for earnings year
        # (Uses age 59 because wage index is not available for age 60 year yet)
        index_factor = wage_index_at_59 / wage_index_current

        return covered_earnings * index_factor
