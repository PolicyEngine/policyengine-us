from policyengine_us.model_api import *


class MEHEAPDwellingType(Enum):
    STICK_BUILT_OR_MODULAR = "Stick-built or modular home"
    MOBILE_OR_MANUFACTURED = "Mobile or manufactured home"
    CONDO_DUPLEX_OR_APARTMENT = "Condominium, duplex or apartment"


class me_heap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = MEHEAPDwellingType
    default_value = MEHEAPDwellingType.STICK_BUILT_OR_MODULAR
    definition_period = YEAR
    label = "Maine HEAP dwelling type"
    documentation = (
        "Dwelling row of the Maine HEAP points matrix: a stick-built or modular "
        "home; a mobile or manufactured home; or a condominium, duplex or "
        "apartment, which share the same points. Defaults to a stick-built or "
        "modular home."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ME_BenefitMatrix_2026.pdf#page=1",
        "https://www.mainehousing.org/docs/default-source/msha-rules/ch24-home-energy-assistance-program-rule.pdf#page=16",
    )
