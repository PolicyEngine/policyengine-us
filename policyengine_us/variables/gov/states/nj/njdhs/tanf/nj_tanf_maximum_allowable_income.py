from policyengine_us.model_api import *


class nj_tanf_maximum_allowable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Jersey TANF maximum allowable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(spm_unit, period, parameters):
        # Get number of people in SPM unit.
        people = spm_unit("spm_unit_size", period)
        # Cap them at the maximum specified in the tables.
        capped_people = min_(people, 8).astype(int)
        # Calculate additional people beyond the maximum in tables.
        additional_people = people - capped_people
        
        # Get the relevant part of the parameter tree.
        p = parameters(period).gov.states.ny.otda.tanf.need_standard
        # Look up the main need standard for the number of (capped) people.
        base = p.main[capped_people]
        # Add the additional need standard for the additional people.
        additional_need_standard = p.additional * additional_people
        monthly = base + additional_need_standard
        # Return annual value.
        return monthly * MONTHS_IN_YEAR
