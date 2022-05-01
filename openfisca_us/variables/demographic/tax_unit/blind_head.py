from openfisca_us.model_api import *


class blind_head(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit head is blind"
    documentation = "True if taxpayer is blind; otherwise False"
