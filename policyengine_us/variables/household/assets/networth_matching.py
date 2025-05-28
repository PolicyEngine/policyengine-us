from policyengine_us.model_api import *


class networth_matching(Variable):
    value_type = float
    entity = Household
    label = "net worth (imputed with statistical matching)"
    unit = USD
    definition_period = YEAR
    uprating = "parameters.gov.bls.cpi.cpi_u"
