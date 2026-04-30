from policyengine_us.model_api import *


class MISSPLivingArrangement(Enum):
    INDEPENDENT_LIVING = "Independent living"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    DOMICILIARY_CARE = "Adult foster care - domiciliary care"
    PERSONAL_CARE = "Adult foster care - personal care"
    HOME_FOR_AGED = "Home for the aged"
    INSTITUTION = "Institution"
    NONE = "Not in a qualifying arrangement"


class mi_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Michigan SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.MI
    possible_values = MISSPLivingArrangement
    default_value = MISSPLivingArrangement.INDEPENDENT_LIVING
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=1",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/BP/Public/BEM/660.pdf#page=4",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/RF/Public/RFT/248.pdf#page=2",
    )
