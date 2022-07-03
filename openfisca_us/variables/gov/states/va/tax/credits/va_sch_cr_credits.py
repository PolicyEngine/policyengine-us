from openfisca_us.model_api import *


class va_sch_cr_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia schedule CR credits"
    unit = USD
    definition_period = YEAR

