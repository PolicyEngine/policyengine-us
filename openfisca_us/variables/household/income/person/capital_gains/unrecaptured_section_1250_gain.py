from openfisca_us.model_api import *


class unrecaptured_section_1250_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Un-recaptured section 1250 gain"
    unit = USD
    definition_period = YEAR
