from policyengine_us.model_api import *


class MDPAALivingArrangement(Enum):
    CARE_HOME_LEVEL_A = "CARE Home Level A"
    CARE_HOME_LEVEL_B = "CARE Home Level B"
    CARE_HOME_LEVEL_C = "CARE Home Level C"
    CARE_HOME_LEVEL_D = "CARE Home Level D"
    ASSISTED_LIVING = "Licensed Assisted Living"
    REHAB_RESIDENCE = "MDH Rehabilitative Residence"
    NONE = "None"


class md_paa_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Maryland PAA living arrangement"
    definition_period = MONTH
    defined_for = StateCode.MD
    possible_values = MDPAALivingArrangement
    default_value = MDPAALivingArrangement.NONE
    reference = (
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20300%20Technical%20Eligibility%20rev%2011.22.docx",
        "https://dhs.maryland.gov/documents/FIA/Manuals/Public%20Assistance%20to%20Adults%20%28PAA%29%20Manual/PAA%20400%20Allowable%20Needs%20rev%2011.22.docx",
        "https://dhs.maryland.gov/documents/FIA/Action%20Transmittals-AT%20-%20Information%20Memo-IM/AT-IM2023/23-02%20AT%20-%20COLA%20Mass%20Mod%20FFY23.pdf#page=3",
    )
