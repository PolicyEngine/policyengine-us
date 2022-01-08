from openfisca_us.model_api import *


class tax_unit_weight(Variable):
    value_type = float
    entity = TaxUnit
    label = u"Tax unit weight"
    definition_period = YEAR
