from openfisca_us.model_api import *


class family_id(Variable):
    value_type = float
    entity = Family
    label = u"Unique reference for this family"
    definition_period = ETERNITY
