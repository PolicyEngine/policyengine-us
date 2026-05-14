from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)


class DCOSSPLivingArrangement(Enum):
    OS_A = "Adult foster care home with 50 beds or less"
    OS_B = "Adult foster care home with over 50 beds"
    OS_G = "Medicaid facility"
    NONE = "Not in a qualifying facility"


class dc_ossp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "DC OSSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.DC
    possible_values = DCOSSPLivingArrangement
    default_value = DCOSSPLivingArrangement.NONE
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.49",
        "https://www.ssa.gov/pubs/EN-05-11162.pdf#page=2",
    )

    def formula(person, period, parameters):
        federal_la = person("ssi_federal_living_arrangement", period.this_year)
        in_medical_facility = (
            federal_la == SSIFederalLivingArrangement.MEDICAL_TREATMENT_FACILITY
        )
        in_afc = person("dc_ossp_in_adult_foster_care", period.this_year)
        facility_size = person("dc_ossp_facility_size", period.this_year)
        p = parameters(period).gov.states.dc.dhcf.ossp
        small_facility = facility_size <= p.facility_size_threshold

        return select(
            [
                in_afc & small_facility,
                in_afc & ~small_facility,
                ~in_afc & in_medical_facility,
            ],
            [
                DCOSSPLivingArrangement.OS_A,
                DCOSSPLivingArrangement.OS_B,
                DCOSSPLivingArrangement.OS_G,
            ],
            default=DCOSSPLivingArrangement.NONE,
        )
