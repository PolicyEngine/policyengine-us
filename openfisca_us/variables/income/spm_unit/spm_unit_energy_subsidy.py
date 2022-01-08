from openfisca_us.model_api import *


class spm_unit_energy_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit school energy subsidy"
    definition_period = YEAR
    unit = USD
