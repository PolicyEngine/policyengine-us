from policyengine_us.model_api import *


class spm_unit_energy_subsidy_reported(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit school energy subsidy (reported)"
    definition_period = YEAR
    unit = USD
