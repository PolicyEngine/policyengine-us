from openfisca_us.model_api import *


class amt_form_completed(Variable):
    value_type = bool
    entity = TaxUnit
    label = "AMT form completed"
    unit = USD
    definition_period = YEAR
