from policyengine_us.model_api import *


class AKSSPLivingArrangement(Enum):
    INDEPENDENT = "Living independently"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    ASSISTED_LIVING = "Assisted living home"
    MEDICAID_FACILITY = "Medicaid facility"


class ak_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Household
    label = "Alaska Adult Public Assistance living arrangement"
    definition_period = YEAR
    defined_for = StateCode.AK
    possible_values = AKSSPLivingArrangement
    default_value = AKSSPLivingArrangement.INDEPENDENT
    reference = (
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ak.pdf#page=2"
    )
