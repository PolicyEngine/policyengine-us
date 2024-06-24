from policyengine_us.model_api import *

class HOMECategory(Enum):
  SINGLE = 'Single Family Home'
  APARTMENT = 'Apartment'

class Home_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "Home category"
  definition_period = YEAR
  possible_values = HOMECategory
  default_value = HOMECategory.ccASHP