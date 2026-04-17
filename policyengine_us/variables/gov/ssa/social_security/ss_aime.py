from policyengine_us.model_api import *
import numpy as np


class ss_aime(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    defined_for = "ss_aime_eligible"
    label = "Average Indexed Monthly Earnings (AIME)"
    documentation = (
        "Average Indexed Monthly Earnings for Social Security "
        "benefit calculation. Uses ss_aime_input when provided, "
        "otherwise computes from earnings history."
    )
    unit = USD
    reference = (
        "https://www.ssa.gov/OACT/COLA/aime.html",
        "https://www.law.cornell.edu/uscode/text/42/415#b",
    )

    def formula(person, period, parameters):
        # Check for direct AIME input override
        aime_input = person("ss_aime_input", period)
        has_input = aime_input > 0

        # Compute AIME from earnings history
        computed_aime = _compute_aime(person, period, parameters)

        return where(has_input, aime_input, computed_aime)


def _compute_aime(person, period, parameters):
    age = person("age", period)
    current_year = period.start.year

    p = parameters(period).gov.ssa.social_security.aime

    birth_year = current_year - age
    indexing_year = birth_year + p.indexing_age
    all_indexed_earnings = []

    lookback = parameters(period).gov.simulation.aime_lookback_years

    for years_ago in range(0, lookback + 1):
        year = current_year - years_ago
        person_age_in_year = age - years_ago
        mask = (person_age_in_year >= p.minimum_age_for_earnings) & (
            person_age_in_year <= p.max_earnings_age
        )

        if np.any(mask):
            year_period = period.this_year.offset(-int(years_ago))

            employment_income = person("employment_income", year_period)
            self_employment_income = person("self_employment_income", year_period)
            total_earnings = employment_income + self_employment_income

            wage_base = parameters(year_period).gov.ssa.social_security.wage_base
            covered_earnings = min_(total_earnings, wage_base)

            indexed_amount = np.zeros_like(covered_earnings)

            needs_indexing = mask & (year <= indexing_year)
            no_indexing = mask & (year > indexing_year)

            if np.any(needs_indexing):
                year_nawi = parameters(year_period).gov.ssa.nawi

                for unique_idx_year in np.unique(indexing_year[mask].astype(int)):
                    idx_mask = (
                        mask
                        & needs_indexing
                        & (indexing_year.astype(int) == unique_idx_year)
                    )

                    if np.any(idx_mask) and unique_idx_year <= current_year:
                        idx_years_ago = current_year - unique_idx_year
                        if idx_years_ago >= 0:
                            idx_period = period.this_year.offset(-int(idx_years_ago))
                            idx_nawi = parameters(idx_period).gov.ssa.nawi
                            indexed_amount[idx_mask] = covered_earnings[idx_mask] * (
                                idx_nawi / year_nawi
                            )

            indexed_amount[no_indexing] = covered_earnings[no_indexing]
            indexed_amount[~mask] = 0
            all_indexed_earnings.append(indexed_amount)

    if all_indexed_earnings:
        earnings_matrix = np.column_stack(all_indexed_earnings)
    else:
        earnings_matrix = np.zeros((person.count, 1))

    sorted_earnings = np.sort(earnings_matrix, axis=1)[:, ::-1]

    top_n = min(sorted_earnings.shape[1], p.years_of_earnings)
    top_earnings = sorted_earnings[:, :top_n]

    if top_n < p.years_of_earnings:
        padding = np.zeros((person.count, p.years_of_earnings - top_n))
        top_earnings = np.hstack([top_earnings, padding])

    total_indexed = np.sum(top_earnings, axis=1)
    return total_indexed / (p.years_of_earnings * p.months_per_year)
