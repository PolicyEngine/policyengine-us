from policyengine_us.model_api import *


class state_and_local_personal_property_taxes(Variable):
    value_type = float
    entity = Person
    label = "State and local personal property taxes"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
