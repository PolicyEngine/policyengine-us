from openfisca_us.model_api import *


class is_ssi_couple(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        "Supplemental Security Income couple with both spouses eligible"
    )
    label = "Supplemental Security Income countable income"
    unit = USD
