from policyengine_us.model_api import *

class DESCRIPTIONCategory(Enum):
    C2 = 'Multifamily Full Load ASHP Heating with Decommissioning'
    C4 = 'Custom Space Heating Applications'
    C4A1 = 'Custome Space Heating Applications + Envelope -- Tier 1'
    C4A2 = 'Custome Space Heating Applications + Envelope -- Tier 2'
    C6 = 'Custom Domestic Hot Water'
    C6A = 'Precscriptive Domestic Hot Water'
    C10 = 'Custom Partial Load Space Heating Applications'


class Description_category(Variable):
  value_type = Enum
  entity = TaxUnit
  label = "Description category"
  definition_period = YEAR
  possible_values = DESCRIPTIONCategory
  default_value = DESCRIPTIONCategory.C2