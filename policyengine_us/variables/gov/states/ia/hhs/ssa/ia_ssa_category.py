from policyengine_us.model_api import *


class IASSACategory(Enum):
    REGULAR = "Ordinary living arrangement"
    DEPENDENT_PERSON = "Certified dependent-person household"
    FAMILY_LIFE_HOME = "Certified family-life home"
    RESIDENTIAL_CARE = "Approved residential care facility"
    IN_HOME_CARE = "Approved in-home health-related care"
    SMME = "Supplement for Medicare and Medicaid eligibles"
    NONE = "No eligible supplementary assistance arrangement"


class ia_ssa_category(Variable):
    value_type = Enum
    entity = Person
    label = "Iowa State Supplementary Assistance category"
    definition_period = MONTH
    possible_values = IASSACategory
    default_value = IASSACategory.REGULAR
    # PDF pages 5-6, 20, 24, 30, 41, 59, 76
    reference = "https://hhs.iowa.gov/media/3987/download?inline=#page=5"
    documentation = """
    Special categories require agency certification of the dependency or care
    arrangement, benefit pursuit, and procedural eligibility. DEPENDENT_PERSON
    requires a selected co-resident relative who is ineligible for SSI/FIP,
    satisfies the marital restrictions and does not deem income to the client.
    Select it for both members of an eligible SSI couple sharing one dependent.
    For residential care reflect separate SSI claims after the entry month.
    NONE also excludes the blind allowance; otherwise it may accompany care.
    """
