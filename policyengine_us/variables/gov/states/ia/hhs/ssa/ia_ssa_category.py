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
    # PDF pages 5-6, 20, 24, 30, 40-41, 57-61, 76
    reference = "https://hhs.iowa.gov/media/3987/download?inline=#page=5"
    documentation = """
    Special categories require agency certification of the dependency or care
    arrangement, benefit pursuit, and procedural eligibility. DEPENDENT_PERSON
    requires a selected co-resident relative who is ineligible for SSI/FIP,
    satisfies the marital restrictions and does not deem income to the client.
    For an eligible SSI couple sharing one dependent, certifying either member
    applies the couple level. Certification also covers the dependent's own
    resources, which 441 IAC 51.5(2) counts with the recipient's; the model
    tests only the recipient's and spouse's resources.
    For residential care, set ia_ssa_care_initial_partial_month in the month
    of entry; a married resident is budgeted alone from the next month. If
    spouses enter separate facilities, ia_ssa_rcf_received_ssi_before_entry
    records prior SSI receipt for their entry-month couple budget. Without
    prior SSI, the same-month couple entry rule also requires
    ia_ssa_rcf_shares_room_with_spouse.
    NONE also excludes the blind allowance; otherwise it may accompany care.
    """
