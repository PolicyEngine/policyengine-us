from policyengine_us.model_api import *


class MDMEAPDwellingType(Enum):
    STANDARD = "Standard residence"
    SUB_METERED = "Submetered residence"
    ASSISTED_LIVING = "Assisted living facility"


class md_meap_dwelling_type(Variable):
    value_type = Enum
    possible_values = MDMEAPDwellingType
    default_value = MDMEAPDwellingType.STANDARD
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP dwelling arrangement"
    reference = (
        "https://dhs.maryland.gov/documents/OHEP/Advisory%20Board/FY26-MEAP-Benefit-Matrix-2-1-1.pdf",
        "https://regs.maryland.gov/us/md/exec/comar/07.03.21.06#D(3)(k)",
    )
    documentation = "Submetered homes use the published Level 6 payment; assisted-living applicants are ineligible under COMAR 07.03.21.06D(3)(k). Ordinary subsidized homes use the existing housing-assistance inputs."
