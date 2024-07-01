from policyengine_us.model_api import *

class DESCRIPTIONCategory(Enum):
    C2 = 'Multifamily Full Load ASHP Heating with Decommissioning'
    C4 = 'Custom Space Heating Applications'
    C4A1 = 'Custome Space Heating Applications + Envelope -- Tier 1'
    C4A2 = 'Custome Space Heating Applications + Envelope -- Tier 2'
    C6 = 'Custom Domestic Hot Water'
    C6A = 'Precscriptive Domestic Hot Water'
    C10 = 'Custom Partial Load Space Heating Applications'


class ny_clean_heat_description_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "New York Clean Heat Description category"
  documentation = "The description category for classifying clean heat program incentives"
  definition_period = YEAR
  reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=13"
  possible_values = DESCRIPTIONCategory
  default_value = DESCRIPTIONCategory.C2
  defined_for = StateCode.NY