from openfisca_us.model_api import *


class mo_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://revisor.mo.gov/main/OneSection.aspx?section=143.111&bid=7201&hl="
