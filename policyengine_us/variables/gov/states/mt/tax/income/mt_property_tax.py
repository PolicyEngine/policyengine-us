from policyengine_us.model_api import *


class mt_property_tax(Variable):
    value_type = float
    entity = Person
    label = "Montana property tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
