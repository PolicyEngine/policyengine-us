from openfisca_us.model_api import *


class receives_housing_assistance(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Currently receives housing assistance"
    documentation = "Currently receives housing assistance"
    definition_period = YEAR
