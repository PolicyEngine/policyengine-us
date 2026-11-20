from policyengine_us.model_api import *


class RILIHEAPElectricityProvider(Enum):
    RHODE_ISLAND_ENERGY = "Rhode Island Energy (Narragansett Electric)"
    BLOCK_ISLAND_UTILITY_DISTRICT = "Block Island Utility District"
    CLEAR_RIVER_ELECTRIC_AND_WATER_DISTRICT = (
        "Clear River Electric and Water District (formerly Pascoag)"
    )
    UNSPECIFIED = "Unspecified"


class ri_liheap_electricity_provider(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = RILIHEAPElectricityProvider
    default_value = RILIHEAPElectricityProvider.UNSPECIFIED
    definition_period = YEAR
    label = "Rhode Island LIHEAP electricity provider"
    documentation = (
        "Company providing the home's electric distribution service, as named "
        "on the electric bill. Rhode Island pays no LIHEAP enhancement on "
        "Block Island Utility District or Clear River Electric and Water "
        "District accounts. UNSPECIFIED (the default) means the company was "
        "not reported and is treated as a qualifying account. This input does "
        "not imply account ownership or receipt of a grant."
    )
    defined_for = StateCode.RI
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE39/39-1/39-1-27.12.htm",
        "https://ripuc.ri.gov/utility-information/regulated-utilities",
    )
