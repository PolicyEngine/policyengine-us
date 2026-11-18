from policyengine_us.model_api import *
from policyengine_us.tools.general import has_input_for_period


class in_ala(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Alameda County"

    def formula(household, period):
        simulation = household.simulation
        # The general county fallback picks Alameda for missing or invalid
        # California FIPS codes. Local aid requires county evidence per row.
        county_fips = np.asarray(household("county_fips", period)).astype(str)
        in_alameda = county_fips == "06001"
        county_supplied = has_input_for_period(simulation, "county", period)
        if simulation.is_over_dataset:
            holder = simulation.get_holder("county")
            county_supplied |= bool(holder.get_input_periods(simulation.branch_name))
        if county_supplied:
            county = household("county", period).decode_to_str()
            in_alameda = where(
                county != "UNKNOWN", county == "ALAMEDA_COUNTY_CA", in_alameda
            )

        if has_input_for_period(simulation, "county_str", period):
            county = np.asarray(household("county_str", period)).astype(str)
            known = (county != "") & (county != "UNKNOWN")
            in_alameda = where(known, county == "ALAMEDA_COUNTY_CA", in_alameda)
        return in_alameda
