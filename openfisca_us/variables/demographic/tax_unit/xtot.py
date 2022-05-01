from openfisca_us.model_api import *


class xtot(Variable):
    value_type = int
    entity = TaxUnit
    definition_period = YEAR
    label = "Filing unit exemptions"
    documentation = "Total number of exemptions for filing unit"
