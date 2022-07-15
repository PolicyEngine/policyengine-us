from openfisca_us.model_api import *


class md_dependent_care_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD depdendent care subtraction from AGI"
    unit = USD
    definition_period = YEAR
