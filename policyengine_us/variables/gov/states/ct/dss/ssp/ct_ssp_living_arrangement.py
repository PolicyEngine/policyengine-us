from policyengine_us.model_api import *


# Not modeled: New Horizons Village — a specific independent living
# facility in Connecticut with its own PNA ($156.82) and DSS-set
# per diem rate.  Small population; requires facility-rate input
# to model correctly.
class CTSSPLivingArrangement(Enum):
    COMMUNITY_ALONE = "Community - Living Alone"
    COMMUNITY_SHARED = "Community - Shared Living"
    BOARDING_HOME = "Boarding Home / Residential Care Home"
    MEDICAID_FACILITY = "Medicaid facility"


class ct_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Connecticut SSP living arrangement"
    definition_period = YEAR
    defined_for = StateCode.CT
    possible_values = CTSSPLivingArrangement
    default_value = CTSSPLivingArrangement.COMMUNITY_ALONE
    reference = (
        "https://www.ctdssmap.com/CTPortal/Information/Get/UPM#4520.10",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period):
        arrangement = person("ssi_federal_living_arrangement", period)
        in_medical_facility = (
            arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        in_boarding_home = person("ct_ssp_resides_in_boarding_home", period)
        lives_with_others = person("ct_ssp_lives_with_others", period)

        LA = CTSSPLivingArrangement
        return select(
            [in_medical_facility, in_boarding_home, lives_with_others],
            [LA.MEDICAID_FACILITY, LA.BOARDING_HOME, LA.COMMUNITY_SHARED],
            default=LA.COMMUNITY_ALONE,
        )
