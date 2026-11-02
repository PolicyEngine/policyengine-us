from policyengine_us.model_api import *


class VTLIHEAPDwellingType(Enum):
    SINGLE_FAMILY_OR_MOBILE_HOME = "Single-family home or mobile home"
    MULTI_FAMILY = "Multi-family home"


class vt_liheap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = VTLIHEAPDwellingType
    default_value = VTLIHEAPDwellingType.SINGLE_FAMILY_OR_MOBILE_HOME
    definition_period = YEAR
    label = "Vermont LIHEAP dwelling type"
    documentation = (
        "Dwelling group of the Vermont standard heating cost tables: a "
        "single-family home (including a modular home) or mobile home, or a "
        "multi-family home such as a duplex, apartment, condo or townhouse. "
        "Defaults to the single-family or mobile home table."
    )
    reference = (
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2916.pdf#page=1",
        "https://outside.vermont.gov/dept/DCF/Policies%20Procedures%20Guidance/ESD-Procedure-P2927B.pdf#page=1",
    )
