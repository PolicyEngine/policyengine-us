from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.geographic.county.county_enum import (
    County,
)
from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)


class first_county_in_state(Variable):
    value_type = Enum
    possible_values = County
    default_value = County.UNKNOWN
    entity = Household
    label = "First county alphabetically in household's state"
    definition_period = YEAR

    def formula(household, period, parameters):
        # Get state codes as strings
        state_code_str = household("state_code_str", period)

        # Build mapping of state abbreviations to first county
        state_to_first_county = {}

        for state in StateCode:
            state_abbr = state.value  # e.g., "CA", "TX", etc.

            # Find all counties for this state
            state_counties = [
                county
                for county in County
                if county != County.UNKNOWN
                and county.value.endswith(f", {state_abbr}")
            ]

            # Sort alphabetically and get the first one
            if state_counties:
                first_county = min(state_counties, key=lambda c: c.value)
                state_to_first_county[state_abbr] = first_county

        # Map each household's state to its first county
        result = []
        for state_abbr in state_code_str:
            county = state_to_first_county.get(state_abbr, County.UNKNOWN)
            result.append(county)

        return np.array(result)
