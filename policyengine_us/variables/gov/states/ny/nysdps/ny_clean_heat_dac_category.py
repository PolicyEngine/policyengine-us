from policyengine_us.model_api import *

class DACCategory(Enum):
  DAC = 'DAC'
  NDAC = 'Non-DAC'

class ny_clean_heat_DAC_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "DAC category"
  documentation = "The DAC category for classifying clean heat program incentives"
  definition_period = YEAR
  reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
  possible_values = DACCategory
  default_value = DACCategory.NDAC