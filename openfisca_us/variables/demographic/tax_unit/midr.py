from openfisca_us.model_api import *


class midr(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Separate filer itemizes"
    documentation = (
        "True if separately-filing spouse itemizes, otherwise false"
    )
