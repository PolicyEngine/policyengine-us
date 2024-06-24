from policyengine_us.model_api import *

class HPCategory(Enum):
  ASHP = 'air source heat pump'
  GSHP = 'ground source heat pump'

class Heat_Pump_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "Heat Pump category"
  definition_period = YEAR
  possible_values = HPCategory
  default_value = HPCategory.ASHP