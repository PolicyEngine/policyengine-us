from openfisca_us.model_api import *


class lives_separately(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Indicates whether a married couple lives separately the whole year."
