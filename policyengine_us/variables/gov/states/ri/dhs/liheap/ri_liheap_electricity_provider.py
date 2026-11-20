from policyengine_us.model_api import *


class RILIHEAPElectricityProvider(Enum):
    # The electric distribution company named on the bill. Block Island and
    # Clear River accounts receive no LIHEAP enhancement.
    RHODE_ISLAND_ENERGY = "Rhode Island Energy (Narragansett Electric)"
    BLOCK_ISLAND_UTILITY_DISTRICT = "Block Island Utility District"
    CLEAR_RIVER_ELECTRIC_AND_WATER_DISTRICT = (
        "Clear River Electric and Water District (formerly Pascoag)"
    )
    # The company was not reported. It is treated as a qualifying account.
    UNSPECIFIED = "Unspecified"


class ri_liheap_electricity_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = RILIHEAPElectricityProvider
    default_value = RILIHEAPElectricityProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Rhode Island LIHEAP electricity provider"
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE39/39-1/39-1-27.12.htm",
        "https://ripuc.ri.gov/utility-information/regulated-utilities",
    )
