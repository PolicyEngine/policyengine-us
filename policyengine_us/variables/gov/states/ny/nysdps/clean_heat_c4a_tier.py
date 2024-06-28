# maybe not needed anymore
from policyengine_us.model_api import *


class CleanHeatC4ATier(Enum):
    One = ">5 percent reduction in dominant load compared to baseline"
    Two = ">30 percent (existing building) or >5 percent (new construction) reduction in dominant load compared to baseline"

class clean_heat_c4a_tier(Variable):
    value_type = Enum
    entity = Household
    label = "Custom Space Heating Applications tiers of envelope upgrade improvements"
    documentation = "Tiers for Category 4 heat pump installation with significant envelope upgrade"
    definition_period = YEAR
    defined_for = StateCode.NY
    reference = "https://cleanheat.ny.gov/assets/pdf/CHG&E%20NGrid%20NYSEG%20O&R%20and%20RG&E%20Program%20Manual_3.1.2024.pdf" # (4.2)(4.3)(4.4)