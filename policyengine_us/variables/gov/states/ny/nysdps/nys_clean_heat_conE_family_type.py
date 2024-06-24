from policyengine_us.model_api import *

class FAMCategory(Enum):
  RESIDENTIAL = 'Residential'
  MULTIFAMILY = 'Multifamily'

class familytype_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "Family Type category"
  definition_period = YEAR
  possible_values = FAMCategory
  default_value = FAMCategory.NONE