from policyengine_us.model_api import *

class DACCategory(Enum):
  DAC = 'DAC'
  NDAC = 'Non-DAC'

class DAC_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "DAC category"
  definition_period = YEAR
  possible_values = DACCategory
  default_value = DACCategory.NDAC