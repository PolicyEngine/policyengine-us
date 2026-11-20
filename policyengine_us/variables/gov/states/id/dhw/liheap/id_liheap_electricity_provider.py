from policyengine_us.model_api import *


class IDLIHEAPElectricityProvider(Enum):
    IDAHO_POWER = "Idaho Power"
    AVISTA = "Avista"
    BONNERS_FERRY_LIGHT_AND_WATER = "Bonners Ferry Light and Water"
    CLEARWATER_POWER = "Clearwater Power"
    IDAHO_COUNTY_LIGHT_AND_POWER = "Idaho County Light and Power"
    INLAND_POWER_AND_LIGHT = "Inland Power and Light"
    KOOTENAI_ELECTRIC = "Kootenai Electric Cooperative"
    NORTHERN_LIGHTS = "Northern Lights Incorporated"
    PLUMMER_ELECTRIC = "Plummer Electric Department"
    ROCKY_MOUNTAIN_POWER = "Rocky Mountain Power"
    OTHER = "Other electricity provider"
    UNSPECIFIED = "Unspecified"


class id_liheap_electricity_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = IDLIHEAPElectricityProvider
    default_value = IDLIHEAPElectricityProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Idaho LIHEAP electricity provider"
    documentation = (
        "Company providing the home's electric service, as named on the "
        "electric bill. It selects the electric column of the Idaho LIHEAP "
        "heating matrix and estimated heating costs: Idaho Power and southern "
        "utilities, Avista and northern utilities, or Rocky Mountain Power. "
        "OTHER means a reported company outside the listed choices and "
        "UNSPECIFIED (the default) means the company was not reported; both "
        "use the Idaho Power and southern utilities column."
    )
    defined_for = StateCode.ID
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://web.archive.org/web/20170127123014id_/http://www.healthandwelfare.idaho.gov/Portals/_Rainbow/Manuals/LIHEAP/Appendices/c_htgcost_matrix_PY07.pdf#page=1",
        "https://oemr.idaho.gov/utilities/",
    )
