from policyengine_us.model_api import *


class MNMSALivingArrangement(Enum):
    INDIVIDUAL_LIVING_ALONE = "Individual living alone"
    INDIVIDUAL_LIVING_WITH_OTHERS = "Individual living with others"
    COUPLE_LIVING_ALONE = "Couple living alone"
    COUPLE_LIVING_WITH_OTHERS = "Couple living with others"
    MEDICAID_FACILITY = "Medicaid facility"
    NONE = "Not in a qualifying arrangement"


class mn_msa_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Minnesota Supplemental Aid living arrangement"
    definition_period = MONTH
    defined_for = StateCode.MN
    possible_values = MNMSALivingArrangement
    default_value = MNMSALivingArrangement.INDIVIDUAL_LIVING_ALONE
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=6",
    )
