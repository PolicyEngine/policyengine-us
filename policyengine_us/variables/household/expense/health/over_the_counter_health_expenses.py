from policyengine_us.model_api import *


class over_the_counter_health_expenses(Variable):
    value_type = float
    entity = Person
    label = "Over the counter health expenses"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
