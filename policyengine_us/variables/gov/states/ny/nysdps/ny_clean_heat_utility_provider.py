from policyengine_us.model_api import *


class UtilityProvider(Enum):
    CH = "Central Hudson"
    NG = "National Grid"
    SEGRGE = "NYSEG/RG&E"
    OR = "Orange & Rockland"


class ny_clean_heat_utility_provider(Variable):
    value_type = Enum
    entity = Household
    label = "New York State Energy Company/Utility Provider"
    reference = [
        "https://cleanheat.ny.gov/assets/pdf/CHG&E%20NGrid%20NYSEG%20O&R%20and%20RG&E%20Program%20Manual_3.1.2024.pdf#page=7",
        "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=6",
    ]
    definition_period = YEAR
    defined_for = StateCode.NY
    possible_values = UtilityProvider
    default_value = UtilityProvider.CH
