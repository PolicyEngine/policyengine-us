from policyengine_us.model_api import *


class ElectricityProvider(Enum):
    UNSPECIFIED = "Unspecified"
    AMEREN_ILLINOIS = "Ameren Illinois"
    AVISTA = "Avista"
    BLOCK_ISLAND_UTILITY_DISTRICT = "Block Island Utility District"
    BONNERS_FERRY_LIGHT_AND_WATER = "Bonners Ferry Light and Water"
    CLEAR_RIVER_ELECTRIC_AND_WATER_DISTRICT = (
        "Clear River Electric and Water District (formerly Pascoag)"
    )
    CLEARWATER_POWER = "Clearwater Power"
    COMED = "ComEd"
    IDAHO_COUNTY_LIGHT_AND_POWER = "Idaho County Light and Power"
    IDAHO_POWER = "Idaho Power"
    INLAND_POWER_AND_LIGHT = "Inland Power and Light"
    KOOTENAI_ELECTRIC = "Kootenai Electric Cooperative"
    NORTHERN_LIGHTS = "Northern Lights Incorporated"
    PLUMMER_ELECTRIC = "Plummer Electric Department"
    RHODE_ISLAND_ENERGY = "Rhode Island Energy (Narragansett Electric)"
    ROCKY_MOUNTAIN_POWER = "Rocky Mountain Power"
    OTHER = "Other electricity provider"


class electricity_provider(Variable):
    value_type = Enum
    possible_values = ElectricityProvider
    default_value = ElectricityProvider.UNSPECIFIED
    entity = SPMUnit
    definition_period = YEAR
    label = "Electricity utility provider"
    documentation = (
        "Company providing the home's electric distribution service, as named on "
        "the utility bill. Report the distribution utility even when a separate "
        "retailer supplies the energy. UNSPECIFIED means the company was not "
        "reported; OTHER means a reported company outside the listed choices. "
        "Named companies support Idaho, Illinois and Rhode Island heating "
        "assistance. The state mapping includes their service in other states. "
        "This input does not imply program enrollment or bill receipt."
    )
    # A null territory makes the choice available in every state.
    metadata = {
        "states_by_value": {
            "UNSPECIFIED": None,
            "AMEREN_ILLINOIS": ["IL"],
            "AVISTA": ["ID", "MT", "WA"],
            "BLOCK_ISLAND_UTILITY_DISTRICT": ["RI"],
            "BONNERS_FERRY_LIGHT_AND_WATER": ["ID"],
            "CLEAR_RIVER_ELECTRIC_AND_WATER_DISTRICT": ["RI"],
            "CLEARWATER_POWER": ["ID", "OR", "WA"],
            "COMED": ["IL"],
            "IDAHO_COUNTY_LIGHT_AND_POWER": ["ID"],
            "IDAHO_POWER": ["ID", "OR"],
            "INLAND_POWER_AND_LIGHT": ["ID", "WA"],
            "KOOTENAI_ELECTRIC": ["ID", "WA"],
            "NORTHERN_LIGHTS": ["ID", "MT", "WA"],
            "PLUMMER_ELECTRIC": ["ID"],
            "RHODE_ISLAND_ENERGY": ["RI"],
            "ROCKY_MOUNTAIN_POWER": ["ID", "UT", "WY"],
            "OTHER": None,
        }
    }
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ID_BenefitMatrix_Heating_2026.pdf#page=1",
        "https://dceo.illinois.gov/communityservices/utilitybillassistance/howtoapply.html",
        "https://webserver.rilegislature.gov/Statutes/TITLE39/39-1/39-1-27.12.htm",
        "https://oemr.idaho.gov/utilities/",
        # Form EIA-861, 2025 final, Service_Territory_2025 (utility by county).
        "https://www.eia.gov/electricity/data/eia861/",
        # EIA lists PacifiCorp as a whole. This is its Rocky Mountain Power brand.
        "https://www.rockymountainpower.net/about.html",
    )
