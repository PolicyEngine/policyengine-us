from policyengine_us.model_api import *


class DESSPLivingArrangement(Enum):
    RESIDENTIAL_CARE = "Certified adult residential care facility"
    NONE = "None"


class de_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Household
    label = "Delaware SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.DE
    possible_values = DESSPLivingArrangement
    default_value = DESSPLivingArrangement.NONE
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415008PHI"
