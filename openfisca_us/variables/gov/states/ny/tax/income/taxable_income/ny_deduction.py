from openfisca_us.model_api import *


class ny_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/613"
    defined_for = StateCode.NY

