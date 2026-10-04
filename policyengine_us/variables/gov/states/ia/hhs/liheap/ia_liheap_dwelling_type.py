from policyengine_us.model_api import *


class IALIHEAPDwellingType(Enum):
    DETACHED = "Detached dwelling (single-unit structure)"
    ATTACHED_2_TO_4_UNITS = "Building of two to four units"
    ATTACHED_5_OR_MORE_UNITS = "Building of five or more units"


class ia_liheap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = IALIHEAPDwellingType
    default_value = IALIHEAPDwellingType.DETACHED
    definition_period = YEAR
    label = "Iowa LIHEAP dwelling type"
    documentation = (
        "Dwelling category of the Iowa LIHEAP payment matrix: a detached "
        "dwelling (+1 point), a building of two to four units (no adjustment), "
        "or a building of five or more units (-1 point). The manual defines a "
        "detached household as one 'occupying a single-unit dwelling (i.e., not "
        "more than one household residing in the complete structure)' and an "
        "attached household as 'more than one household ... within a single "
        "structure (i.e., multi-unit dwellings such as duplexes, apartments, "
        "etc.)'. Mobile and manufactured homes occupied by one household are "
        "not placed in the matrix; they meet the single-unit definition and are "
        "treated as DETACHED by inference. Defaults to DETACHED."
    )
    reference = (
        # Appendix I matrix (page 137); Definitions, Attached Household (page
        # 79), Detached Household/Single Family Home (page 80) and
        # Mobile/Manufactured Home (page 82).
        "https://hhs.iowa.gov/media/17262/download?inline#page=137",
        # Section 2.5, dwelling type checked as a benefit variable.
        "https://liheapch.acf.gov/docs/2026/state-plans/IA_Plan_2026.pdf#page=9",
    )
