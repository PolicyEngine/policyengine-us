from policyengine_us.model_api import *

class BUILDCategory(Enum):
  NEW = "New Construction"
  EXISTING = "Existing Building"

class Building_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "Building category"
  definition_period = YEAR
  possible_values = BUILDCategory
  default_value = BUILDCategory.NEW