from policyengine_us.model_api import *


class ct_property_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut property tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
