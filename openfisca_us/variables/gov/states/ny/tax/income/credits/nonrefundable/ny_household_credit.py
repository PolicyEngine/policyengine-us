from openfisca_us.model_api import *


class ny_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY household credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (b)
