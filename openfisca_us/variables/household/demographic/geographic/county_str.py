from openfisca_us.model_api import *


class county_str(Variable):
    value_type = str
    entity = Household
    label = "County (string)"
    documentation = "County variable, stored as a string"
    definition_period = ETERNITY

    def formula(household, period, parameters):
        county_name = household("county", period).decode_to_str()
        unknown_county = county_name == "UNKNOWN"

        if any(unknown_county):
            # We don't have full counties - randomly assign zip codes
            population_data = parameters(
                period
            ).demographic.geography.population_by_county
            np.random.seed(0)
            states = np.array(list(population_data._children.keys()))
            state = household("state_code", period)
            for possible_state in states:
                in_state = state == possible_state
                possible_counties = np.array(list(population_data[possible_state]._children.keys()))
                populations = np.array(list(population_data[possible_state]._children.values()))
                county_name[in_state & unknown_county] = (
                    np.random.choice(
                        possible_counties,
                        size=len(county_name[in_state & unknown_county]),
                        p=populations / populations.sum(),
                    )
                    .astype(int)
                    .astype(str)
                )

        return county_name
