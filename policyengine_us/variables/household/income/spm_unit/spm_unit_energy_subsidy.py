from policyengine_us.model_api import *


class spm_unit_energy_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit energy subsidy"
    definition_period = YEAR
    unit = USD
    uprating = "gov.bls.cpi.cpi_u"
