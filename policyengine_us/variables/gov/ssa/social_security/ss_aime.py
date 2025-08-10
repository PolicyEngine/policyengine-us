from policyengine_us.model_api import *
from policyengine_core.periods import Period, instant
import numpy as np


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
        age = person("age", period)
        current_year = period.start.year
        
        # Get parameters
        p = parameters(period).gov.ssa.social_security.aime
        minimum_age_for_earnings = p.minimum_age_for_earnings
        years_of_earnings = p.years_of_earnings
        months_per_year = p.months_per_year
        indexing_age = p.indexing_age
        
        # Calculate birth year and indexing year (vectorized)
        birth_year = current_year - age
        indexing_year = birth_year + indexing_age
        
        # Determine the range of years to consider for each person (vectorized)
        start_year = birth_year + minimum_age_for_earnings
        end_year = min_(current_year, birth_year + 62)  # Stop at age 62 or current year
        
        # Get National Average Wage Index parameters
        nawi = parameters(period).gov.ssa.national_average_wage_index
        
        # Determine the global range of years to process
        min_year = int(np.min(start_year))
        max_year = int(np.max(end_year))
        
        # Initialize list to store indexed earnings for each year
        all_indexed_earnings = []
        
        # Loop through years (not people) and vectorize within each year
        for year in range(min_year, max_year + 1):
            # Create mask for people who had potential earnings in this year
            mask = (year >= start_year) & (year <= end_year)
            
            if np.any(mask):
                # Get earnings for this year (vectorized for all people)
                year_period = period.this_year.offset(year - current_year)
                employment_income = person("employment_income", year_period)
                self_employment_income = person("self_employment_income", year_period)
                total_earnings = employment_income + self_employment_income
                
                # Apply wage base cap
                wage_base = parameters(year_period).gov.ssa.social_security.wage_base
                covered_earnings = min_(total_earnings, wage_base)
                
                # Index earnings to age 60 (vectorized)
                year_nawi = nawi[year_period]
                
                # Determine which people need indexing for this year
                needs_indexing = mask & (year <= indexing_year)
                no_indexing = mask & (year > indexing_year)
                
                # Calculate indexing factors for each person (vectorized)
                indexed_amount = np.zeros_like(covered_earnings)
                
                # For those who need indexing
                if np.any(needs_indexing):
                    # Get the indexing NAWI for each person's indexing year
                    indexing_nawis = np.zeros_like(covered_earnings)
                    for idx_year in np.unique(indexing_year[needs_indexing].astype(int)):
                        idx_mask = needs_indexing & (indexing_year.astype(int) == idx_year)
                        if np.any(idx_mask):
                            idx_period = period.this_year.offset(idx_year - current_year)
                            indexing_nawis[idx_mask] = nawi[idx_period]
                    
                    # Apply indexing (vectorized)
                    indexed_amount[needs_indexing] = covered_earnings[needs_indexing] * (indexing_nawis[needs_indexing] / year_nawi)
                
                # For those after age 60, no indexing
                indexed_amount[no_indexing] = covered_earnings[no_indexing]
                
                # Set to 0 for people outside their earning years
                indexed_amount[~mask] = 0
                
                # Store indexed earnings
                all_indexed_earnings.append(indexed_amount)
        
        # Convert to numpy array (people x years)
        if all_indexed_earnings:
            earnings_matrix = np.column_stack(all_indexed_earnings)
        else:
            earnings_matrix = np.zeros((len(age), 1))
        
        # For each person, take the highest 35 years (vectorized using sorting)
        # Sort each person's earnings in descending order
        sorted_earnings = np.sort(earnings_matrix, axis=1)[:, ::-1]
        
        # Take the top 35 years (or fewer if less than 35 years of earnings)
        top_35_columns = min(sorted_earnings.shape[1], years_of_earnings)
        top_earnings = sorted_earnings[:, :top_35_columns]
        
        # If less than 35 years, pad with zeros
        if top_35_columns < years_of_earnings:
            padding = np.zeros((len(age), years_of_earnings - top_35_columns))
            top_earnings = np.hstack([top_earnings, padding])
        
        # Calculate AIME (vectorized)
        total_indexed = np.sum(top_earnings, axis=1)
        aime_values = total_indexed / (years_of_earnings * months_per_year)
        
        # Return 0 if under minimum working age
        return where(age < minimum_age_for_earnings, 0, aime_values)
