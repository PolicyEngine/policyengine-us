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
        # Division position memo, November 12, 2026: grants go only to
        # Rhode Island Energy customers.
        "https://ripuc.ri.gov/sites/g/files/xkgbur841/files/2026-11/26-34-GE%20LIHEAP%20Enhancement%20-%20DPUC%20Position%20Memo%20%2811-12-26%29.pdf#page=1",
    )
