from openfisca_us.model_api import *


class salt_refund_last_year(Variable):
    value_type = float
    entity = TaxUnit
    label = "SALT refund last year"
    unit = USD
    definition_period = YEAR
