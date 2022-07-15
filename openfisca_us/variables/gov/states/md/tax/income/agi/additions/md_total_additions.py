from openfisca_us.model_api import *


class md_total_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Total Additions"
    unit = USD
    definition_period = YEAR
