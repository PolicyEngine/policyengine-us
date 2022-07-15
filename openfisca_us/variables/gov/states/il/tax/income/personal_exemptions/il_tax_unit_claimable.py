from openfisca_us.model_api import *


class il_tax_unit_claimable(Variable):
    value_type = bool
    entity = Person
    label = "Whether a person can be claimed as a dependent by another filer"
    unit = USD
    definition_period = YEAR
