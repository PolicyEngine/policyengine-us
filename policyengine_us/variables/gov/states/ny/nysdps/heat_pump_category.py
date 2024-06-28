from policyengine_us.model_api import *

class HPCategory(Enum):
    C2 = "ccASHP: Full Load Heating"
    C2A = "ccASHP: Full Load Heating with integrated controls (inclusive of base incentive)"
    C2B = "ccASHP: Full Load Heating with decommissioning (inclusive of base incentive)"
    C2E = "Air-to-Water Heat Pump for space conditioning"
    C3 = "GSHP: Full Load Heating"
    C4 = "Custom Space Heating Applications"
    C4A1 = "Heat Pump + Envelope Tier 1"
    C4A2 = "Heat Pump + Envelope Tier 2"
    C5A = "Residential Rated HPWH: Retail" 
    C5B = "Residential Rated HPWH: Midstream"
    C6 = "Custom Hot Water Heating Applications"
    C7 = "GSHP Desuperheater"
    C8 = "WWHP used for DHW"
    C9 = "Simultaneous Installation of Space Heating & Domestic Water Heating"


class heat_pump_category(Variable):
    value_type = Enum
    entity = Household
    label = "Heat pump technology category"
    documentation = "Heat pump technologies that qualify for Clean Heat incentives."
    definition_period = YEAR
    defined_for = StateCode.NY
    possible_values = HPCategory
    default_value = HPCategory.C2