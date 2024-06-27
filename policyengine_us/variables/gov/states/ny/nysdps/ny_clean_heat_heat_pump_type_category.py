from policyengine_us.model_api import *

class HPTYPECategory(Enum):
  ASHPWIC = 'ccASHP with integrated controls'
  ASHPWDE = 'ccASHP with decommissioning'
  AWHPWDE = 'AWHP with decommissioning'

class ny_clean_heat_heat_pump_type_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "Heat Pump Type category"
  documentation = "The heat pump type category for classifying clean heat program incentives"
  definition_period = YEAR
  reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf#page=12"
  possible_values = HPTYPECategory
  default_value = HPTYPECategory.ASHPWIC
  defined_for = StateCode.NY