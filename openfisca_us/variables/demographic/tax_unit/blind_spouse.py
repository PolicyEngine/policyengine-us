from openfisca_us.model_api import *


class blind_spouse(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax unit spouse is blind"
    documentation = "1 if spouse is blind; otherwise 0"
