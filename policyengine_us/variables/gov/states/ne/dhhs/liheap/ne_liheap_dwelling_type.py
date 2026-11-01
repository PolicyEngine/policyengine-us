from policyengine_us.model_api import *


class NELIHEAPDwellingType(Enum):
    MULTI_FAMILY = "Multi-family arrangement"
    SINGLE_FAMILY = "Single-family arrangement"


class ne_liheap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = NELIHEAPDwellingType
    default_value = NELIHEAPDwellingType.SINGLE_FAMILY
    definition_period = YEAR
    label = "Dwelling type for Nebraska LIHEAP"
    documentation = (
        "Under 476 NAC 1-004.11 and 1-004.16, multi-family means more than one "
        "household occupies a structure, including apartments with separate "
        "energy bills and communal arrangements with shared bills. Single-family "
        "means one household occupies the structure. If omitted, the model "
        "assumes single-family; report the type to apply the correct schedule."
    )
    reference = "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/chapter-pdfs/476%20NAC%201%20(12-26-2020).pdf/1746#page=2"
