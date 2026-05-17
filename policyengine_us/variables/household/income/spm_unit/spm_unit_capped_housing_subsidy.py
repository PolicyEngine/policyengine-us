from policyengine_us.model_api import *


class spm_unit_capped_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing subsidies"
    definition_period = YEAR
    unit = USD
    uprating = "gov.bls.cpi.cpi_u"
