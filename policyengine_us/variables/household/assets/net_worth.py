from policyengine_us.model_api import *


class net_worth(Variable):
    value_type = float
    entity = Household
    label = "net worth"
    unit = USD
    definition_period = YEAR
    uprating = "gov.bls.cpi.cpi_u"
