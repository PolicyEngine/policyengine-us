from policyengine_us.model_api import *

class HPTYPECategory(Enum):
  ccASHPWIC = 'ccASHP with integrated controls'
  ccASHPWDE = 'ccASHP with decommissioning'
  AWHPWDE = 'AWHP with decommissioning'

class Heat_Pump_Type_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "Heat Pump Type category"
  definition_period = YEAR
  possible_values = HPTYPECategory
  default_value = HPTYPECategory.ccASHP