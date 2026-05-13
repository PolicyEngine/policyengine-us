from policyengine_us.model_api import *


class spm_unit_capped_housing_subsidy_data(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit capped housing subsidy from input data"
    definition_period = YEAR
    unit = USD
    uprating = "gov.bls.cpi.cpi_u"
