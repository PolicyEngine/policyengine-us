from policyengine_us.model_api import *


class HeatingType(Enum):
    # Also the right value when heat is included in rent and the tenant
    # does not know the building's fuel: heat_expense_included_in_rent
    # carries the heat-in-rent fact and bypasses the expense cap, so the
    # fuel type is not needed. Never use NONE there — the home has heat.
    UNSPECIFIED = "Unspecified"
    ELECTRICITY = "Electricity"
    NATURAL_GAS = "Natural gas"
    FUEL_OIL = "Fuel oil"
    KEROSENE = "Kerosene"
    PROPANE = "Propane"
    WOOD = "Wood"
    COAL = "Coal"
    SOLAR = "Solar"
    OTHER = "Other"
    NONE = "None"


class heating_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = HeatingType
    default_value = HeatingType.UNSPECIFIED
    label = "Primary home heating fuel type"
    documentation = "The fuel used most to heat the home, adapted from the American Community Survey house heating fuel categories (table B25040): the ACS 'fuel oil, kerosene, etc.' category is split into FUEL_OIL and KEROSENE because Massachusetts rates kerosene separately, utility gas is NATURAL_GAS, and bottled, tank or LP gas is PROPANE. Households heating with several fuels report the primary one; secondary fuel bills stay in their own expense inputs. NONE affirmatively means the home has no heating. UNSPECIFIED (the default) means the fact was not supplied, and programs then fall back to their deprecated pre-canonical arbitration; it is also the right value when heat is included in rent and the fuel is unknown, since the separate heat_expense_included_in_rent input carries that fact. State program fuel categories are derived from this input. A known heating type must be stamped together with the matching per-fuel expense: heating_expense reads only that fuel's bill, so a known type with no bill is a zero heating cost."
    definition_period = YEAR
    reference = "https://data.census.gov/table/ACSDT1Y2023.B25040"
