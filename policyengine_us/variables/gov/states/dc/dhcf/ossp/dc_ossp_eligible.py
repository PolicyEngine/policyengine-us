from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.dc.dhcf.ossp.dc_ossp_living_arrangement import (
    DCOSSPLivingArrangement,
)


class dc_ossp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "DC OSSP eligible"
    definition_period = MONTH
    defined_for = StateCode.DC
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.49",
        "https://www.ssa.gov/pubs/EN-05-11162.pdf#page=2",
    )

    def formula(person, period, parameters):
        # Per POMS SI 01401.001, "state supplement only" cases have
        # countable income above the FBR but below the combined
        # payment level. They receive $0 federal SSI but still
        # qualify for a reduced state supplement. Eligibility is
        # therefore categorical (is_ssi_eligible), not ssi > 0.
        categorically_eligible = person("is_ssi_eligible", period.this_year)
        living_arrangement = person("dc_ossp_living_arrangement", period)
        in_qualifying_facility = living_arrangement != DCOSSPLivingArrangement.NONE
        return categorically_eligible & in_qualifying_facility
