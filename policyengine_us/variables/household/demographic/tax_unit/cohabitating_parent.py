from policyengine_us.model_api import *


class cohabitating_parent(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Cohabitating parents"
    documentation = "Whether parents in the household are cohabitating."
