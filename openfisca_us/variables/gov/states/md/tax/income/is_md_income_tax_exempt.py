from openfisca_us.model_api import *


class is_md_income_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "MD income tax exempt"
    unit = USD
    definition_period = YEAR
    reference = ""
