from policyengine_us.model_api import *


class household_vehicles_equity(Variable):
    value_type = float
    entity = Household
    label = "Vehicle equity"
    documentation = "Net equity in household vehicles after secured vehicle debt."
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
