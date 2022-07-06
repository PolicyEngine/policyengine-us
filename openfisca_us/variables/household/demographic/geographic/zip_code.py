from openfisca_us.model_api import *


class zip_code(Variable):
    value_type = str
    entity = Household
    label = "ZIP code"
    definition_period = YEAR
    default_value = "UNKNOWN"
