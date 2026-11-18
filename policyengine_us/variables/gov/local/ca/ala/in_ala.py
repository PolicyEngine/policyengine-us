from policyengine_us.model_api import *
from policyengine_us.tools.general import has_input_for_period


class in_ala(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Alameda County"

    def formula(household, period):
        simulation = household.simulation
        # A missing or invalid FIPS code defaults to Alameda in California.
        # Local cash assistance requires an identified county.
        if any(
            has_input_for_period(simulation, variable, period)
            for variable in ("county_str", "county")
        ):
            return household("county_str", period) == "ALAMEDA_COUNTY_CA"

        if simulation.is_over_dataset:
            holder = simulation.get_holder("county")
            if holder.get_input_periods(simulation.branch_name):
                return household("county_str", period) == "ALAMEDA_COUNTY_CA"

        return np.asarray(household("county_fips", period)).astype(str) == "06001"
