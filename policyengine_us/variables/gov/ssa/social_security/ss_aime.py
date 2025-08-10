from policyengine_us.model_api import *
import numpy as np


class ss_aime(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    defined_for = "ss_aime_eligible"
    label = "Average Indexed Monthly Earnings (AIME)"
    documentation = "Average Indexed Monthly Earnings for Social Security benefit calculation"
    unit = USD
    reference = (
        "https://www.ssa.gov/OACT/COLA/aime.html",
        "https://www.law.cornell.edu/uscode/text/42/415#b",
    )

    def formula(person, period, parameters):
        age = person("age", period)
        current_year = period.start.year

        # Get parameters
        p = parameters(period).gov.ssa.social_security.aime

        # Calculate birth year and indexing year (vectorized)
        birth_year = current_year - age
        indexing_year = birth_year + p.indexing_age
        all_indexed_earnings = []

        # Loop through years and collect earnings
        for years_ago in range(
            0, parameters(period).gov.simulation.aime_lookback_years + 1
        ):
            # Calculate the year we're looking at
            year = current_year - years_ago

            # Check if this year is in the valid earning range for each person
            person_age_in_year = age - years_ago
            mask = (person_age_in_year >= p.minimum_age_for_earnings) & (
                person_age_in_year <= p.max_earnings_age
            )

            if np.any(mask):
                # Create a period for this year (ensure int type for offset)
                year_period = period.this_year.offset(-int(years_ago))

                # Get earnings for this year directly from input
                employment_income = person("employment_income", year_period)
                self_employment_income = person(
                    "self_employment_income", year_period
                )
                total_earnings = employment_income + self_employment_income

                # Apply wage base cap
                wage_base = parameters(
                    year_period
                ).gov.ssa.social_security.wage_base
                covered_earnings = min_(total_earnings, wage_base)

                # Initialize indexed amount
                indexed_amount = np.zeros_like(covered_earnings)

                # Determine who needs indexing
                # Index earnings if the year is at or before the indexing year (age 60)
                needs_indexing = mask & (year <= indexing_year)
                no_indexing = mask & (year > indexing_year)

                # For those who need indexing
                if np.any(needs_indexing):
                    # Get NAWI for the earnings year
                    year_nawi = parameters(year_period).gov.ssa.nawi

                    # Get NAWI for each person's indexing year
                    # We need to handle each unique indexing year separately
                    for unique_idx_year in np.unique(
                        indexing_year[mask].astype(int)
                    ):
                        # Find people with this indexing year who need indexing
                        idx_mask = (
                            mask
                            & needs_indexing
                            & (indexing_year.astype(int) == unique_idx_year)
                        )

                        if (
                            np.any(idx_mask)
                            and unique_idx_year <= current_year
                        ):
                            # Calculate years ago for indexing year
                            idx_years_ago = current_year - unique_idx_year
                            if idx_years_ago >= 0:
                                idx_period = period.this_year.offset(
                                    -int(idx_years_ago)
                                )
                                idx_nawi = parameters(idx_period).gov.ssa.nawi

                                # Apply indexing formula: earnings * (NAWI_age60 / NAWI_earnings_year)
                                indexed_amount[idx_mask] = covered_earnings[
                                    idx_mask
                                ] * (idx_nawi / year_nawi)

                # For those after age 60, no indexing - use actual covered earnings
                indexed_amount[no_indexing] = covered_earnings[no_indexing]

                # Set to 0 for people outside their earning years
                indexed_amount[~mask] = 0

                # Store indexed earnings
                all_indexed_earnings.append(indexed_amount)

        # Convert to numpy array (people x years)
        if all_indexed_earnings:
            earnings_matrix = np.column_stack(all_indexed_earnings)
        else:
            earnings_matrix = np.zeros((person.count, 1))

        # For each person, take the highest 35 years (vectorized using sorting)
        # Sort each person's earnings in descending order
        sorted_earnings = np.sort(earnings_matrix, axis=1)[:, ::-1]

        # Take the top 35 years (or fewer if less than 35 years of earnings)
        top_35_columns = min(sorted_earnings.shape[1], p.years_of_earnings)
        top_earnings = sorted_earnings[:, :top_35_columns]

        # If less than 35 years, pad with zeros
        if top_35_columns < p.years_of_earnings:
            padding = np.zeros(
                (person.count, p.years_of_earnings - top_35_columns)
            )
            top_earnings = np.hstack([top_earnings, padding])

        # Calculate AIME (vectorized)
        total_indexed = np.sum(top_earnings, axis=1)
        aime_values = total_indexed / (p.years_of_earnings * p.months_per_year)

        return aime_values
