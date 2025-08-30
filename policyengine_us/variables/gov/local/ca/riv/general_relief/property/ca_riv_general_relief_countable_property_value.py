from policyengine_us.model_api import *


class ca_riv_general_relief_countable_property_value(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Riverside County General Relief countable property value"
    definition_period = YEAR
    defined_for = "in_riv"

    adds = "gov.local.ca.riv.general_relief.property.sources"
