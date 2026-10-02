from policyengine_us.model_api import *


class INEAPDwellingType(Enum):
    MOBILE_HOME = "Mobile home"
    MULTI_UNIT = "Multi-unit dwelling (duplex or larger)"
    SINGLE_FAMILY = "Site-built single-family or manufactured home on a foundation"


class in_eap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = INEAPDwellingType
    default_value = INEAPDwellingType.SINGLE_FAMILY
    definition_period = YEAR
    label = "Dwelling type for Indiana EAP"
    documentation = (
        "Section 8.4 classifies a manufactured home on a foundation as "
        "single-family. Multi-unit includes duplexes and apartments. If omitted, "
        "the model assumes single-family; report the type to apply the correct "
        "dwelling points. Heat included in rent is reported separately."
    )
    reference = (
        # Section 8.4 (pages 70-71).
        "https://www.in.gov/ihcda/files/Indiana-LIHEAP-Intake-and-Operations-Program-Manual-PY2026.pdf#page=70",
    )
