from policyengine_us.model_api import *


class NEAABDLivingArrangement(Enum):
    INDEPENDENT = "Living independently"
    LONG_TERM_CARE = "Long-term care (Medicaid facility)"
    BOARD_AND_ROOM = (
        "Board and room facility (also covers Drug Treatment Center, "
        "Licensed/Non-Licensed Boarding Home, and Licensed Center for "
        "the Developmentally Disabled — all share the same rate per "
        "469-000-211)"
    )
    ADULT_FAMILY_HOME = "Certified Adult Family Home"
    ASSISTED_LIVING_FACILITY = (
        "Licensed Assisted Living Facility (also covers Licensed Mental "
        "Health Center — both share the same rate per 469-000-211)"
    )
    ASSISTED_LIVING_WAIVER = "Assisted Living Waiver (AD/TBI)"
    GROUP_HOME_CHILDREN = "Licensed Group Home for Children or Child Caring Agency"
    NONE = "None"


class ne_aabd_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Nebraska AABD living arrangement"
    definition_period = MONTH
    defined_for = StateCode.NE
    possible_values = NEAABDLivingArrangement
    default_value = NEAABDLivingArrangement.NONE
    reference = (
        "https://dhhs.ne.gov/Documents/469-000-211.pdf",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ne.pdf#page=1",
    )

    def formula(person, period):
        federal_arrangement = person("ssi_federal_living_arrangement", period.this_year)
        in_medical_facility = (
            federal_arrangement
            == federal_arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        )
        alternate = person("ne_aabd_alternate_living_arrangement", period.this_year)
        return where(
            in_medical_facility,
            NEAABDLivingArrangement.LONG_TERM_CARE,
            alternate,
        )
