from policyengine_us.model_api import *


class NyCleanHeatHeatPump(Enum):
    C2 = "ccASHP: Full Load Heating"  # (2.1.1)(3.4.2.1-2)
    C2A = "ccASHP: Full Load Heating with integrated controls"  # (2.1.1)(3.4.2.1-2)
    C2B = (
        "ccASHP: Full Load Heating with decommissioning"  # (2.1.1)(3.4.2.1-2)
    )
    C2C = "Multifamily Full Load ASHP Heating with Decommissioning"  # (2.1.1)(3.4.2.1-2)
    C2E = "Air-to-Water Heat Pump for space conditioning with decommissioning"  # (2.1.1)(3.4.2.3)
    C3 = "GSHP: Full Load Heating"  # (2.1.1)(3.4.3)
    C4 = "Custom Space Heating Applications"  # (2.1.1)(3.4.2.4-7)(3.4.3)(3.4.5)(3.4.6)(3.4.7)
    C4A1 = "Custom Space Heating Applications/Heat Pump + Envelope Tier 1"  # (3.4.6)(3.4.7)(3.5)
    C4A2 = "Custom Space Heating Applications/Heat Pump + Envelope Tier 2"  # (3.4.6)(3.4.7)(3.5)
    C5A = "Residential Rated HPWH: Retail"  # (3.4.4.1)
    C5B = "Residential Rated HPWH: Midstream"
    C6 = "Custom Hot Water Heating Applications"  # (3.4.4.1-2)(3.4.6)
    C6A = "Prescriptive Hot Water Heating Applications"  # (ConEd 4.3.2.3)
    C7 = "GSHP Desuperheater"  # (3.4.4.2)
    C8 = "WWHP used for DHW"  # (3.4.4.2)
    C9 = "Simultaneous Installation of Space Heating & Domestic Water Heating"  # (3.3.3)
    C10 = "Custom Partial Load Space Heating Applications"  # (ConEd 4.3.2.3)


class ny_clean_heat_heat_pump_category(Variable):
    value_type = Enum
    entity = Household
    label = "Heat pump technology category"
    documentation = "Heat pump technologies that qualify for Clean Heat program incentives."
    reference = [
        "https://cleanheat.ny.gov/assets/pdf/CHG&E%20NGrid%20NYSEG%20O&R%20and%20RG&E%20Program%20Manual_3.1.2024.pdf#page=10",
        "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=11",
    ]  # (2.1)(3.3)
    definition_period = YEAR
    defined_for = StateCode.NY
    possible_values = NyCleanHeatHeatPump
    default_value = NyCleanHeatHeatPump.C2
