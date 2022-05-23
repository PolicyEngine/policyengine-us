from openfisca_us.model_api import *


class zip_code(Variable):
    value_type = str
    entity = Household
    label = "Zip code"
    definition_period = YEAR
