from policyengine_us.model_api import *


class nc_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF need standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        # Get the relevant part of the parameter tree.
        p = parameters(period).gov.states.nc.ncdhhs.tanf.need_standard
        # Get number of eligible people in SPM unit.
        household_size = spm_unit("nc_tanf_household_size", period)
        # Get household size list
        household_size_list = list(map(int, (p.main)))
        # Get the maximum number of people defined in the tables.
        max_standard_household_size = max(household_size_list)
        # Cap them at the maximum specified in the tables.
        capped_household_size = min_(
            household_size, max_standard_household_size
        ).astype(int)
        # Calculate additional people beyond the maximum in tables.
        additional_people = household_size - capped_household_size
        # Look up the main maximum benefit for the number of (capped) people.
        base = p.main[capped_household_size]
        # Add the additional maximum benefit for the additional people.
        additional_maximum_benefit = p.additional_person * additional_people
        monthly_amount = base + additional_maximum_benefit
        # Return annual value.
        return monthly_amount * MONTHS_IN_YEAR
