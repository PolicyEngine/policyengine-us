from policyengine_us.model_api import *


class networth(Variable):
    value_type = float
    entity = Household
    label = "net worth"
    unit = USD
    definition_period = YEAR
    uprating = "parameters.gov.bls.cpi.cpi_u"
