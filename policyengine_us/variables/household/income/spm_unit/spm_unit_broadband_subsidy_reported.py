from policyengine_us.model_api import *


class spm_unit_broadband_subsidy_reported(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit reported broadband subsidy"
    definition_period = YEAR
    unit = USD
    uprating = "gov.bls.cpi.cpi_u"
