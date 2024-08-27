from policyengine_us.model_api import *


class nc_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF need standard"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        # Get number of people in SPM unit.
        people = spm_unit("spm_unit_size", period)
        # Cap them at the maximum specified in the tables.
        capped_people = min_(people, 14).astype(int)
        # Calculate additional people beyond the maximum in tables.
        additional_people = people - capped_people
        # Get the relevant part of the parameter tree.
        p = parameters(period).gov.states.nc.ncdhhs.tanf.need_standard
        # Look up the main maximum benefit for the number of (capped) people.
        base = p.main[capped_people]
        # Add the additional maximum benefit for the additional people.
        additional_maximum_benefit = p.additional_person * additional_people
        monthly_amount = base + additional_maximum_benefit
        # Return annual value.
        return monthly * MONTHS_IN_YEAR
