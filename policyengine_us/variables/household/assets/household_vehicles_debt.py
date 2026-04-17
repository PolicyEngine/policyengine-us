from policyengine_us.model_api import *


class household_vehicles_debt(Variable):
    value_type = float
    entity = Household
    label = "Vehicle debt"
    documentation = "Outstanding debt secured by household vehicles."
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
