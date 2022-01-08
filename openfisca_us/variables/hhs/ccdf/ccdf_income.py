from openfisca_us.model_api import *


class ccdf_income(Variable):
    value_type = float
    entity = SPMUnit
    label = u"Income"
    definition_period = YEAR
    unit = "currency-USD"
