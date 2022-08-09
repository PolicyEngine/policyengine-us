from openfisca_us.model_api import *


class ny_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/616"
    defined_for = StateCode.NY

