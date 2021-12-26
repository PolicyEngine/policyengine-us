from openfisca_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Supplemental Security Income amount"
    label = "Supplemental Security Income"
    unit = "currency-USD"
