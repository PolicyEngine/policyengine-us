from policyengine_us.model_api import *


class MOSSPLivingArrangement(Enum):
    SAB = "Supplemental Aid to the Blind (own home or facility)"
    RCF_LEVEL_I = "Residential Care Facility Level I"
    RCF_LEVEL_II_OR_ALF = (
        "Residential Care Facility Level II or Assisted Living Facility"
    )
    SNF_OR_ICF_NON_MEDICAID = (
        "Skilled Nursing or Intermediate Care Facility, non-Medicaid"
    )
    NONE = "None of the above"


class mo_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Missouri SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.MO
    possible_values = MOSSPLivingArrangement
    default_value = MOSSPLivingArrangement.NONE
    reference = (
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.030",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/07/mhabd-appendix-j.pdf#page=4",
    )
