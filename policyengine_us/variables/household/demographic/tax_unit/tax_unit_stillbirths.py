from policyengine_us.model_api import *


class tax_unit_stillbirths(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of stillborn children in the filing year"
    definition_period = YEAR
