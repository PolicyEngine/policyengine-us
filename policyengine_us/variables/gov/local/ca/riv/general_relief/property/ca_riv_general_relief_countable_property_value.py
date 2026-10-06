from policyengine_us.model_api import *


class ca_riv_general_relief_countable_property_value(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Riverside County General Relief countable property value"
    definition_period = YEAR
    quantity_type = STOCK
    defined_for = "in_riv"

    # The property limit applies to the unit's combined property. The sources
    # mix unit-level amounts (cash assets, countable vehicle value), which are
    # counted once, with person-level personal property, which is summed over
    # members.
    adds = "gov.local.ca.riv.general_relief.property.sources"
