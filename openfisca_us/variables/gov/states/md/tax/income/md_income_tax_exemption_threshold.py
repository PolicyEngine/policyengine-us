from openfisca_us.model_api import *


class md_income_tax_exemption_threshold(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD income tax exemption threshold"
    unit = USD
    documentation = "MD AGI threshold below which an individual is exempt from State income tax."
    definition_period = YEAR
    reference = ""

    