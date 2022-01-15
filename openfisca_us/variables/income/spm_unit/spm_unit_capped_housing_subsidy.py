from openfisca_us.model_api import *


class spm_unit_capped_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit capped housing subsidy"
    definition_period = YEAR
    unit = USD
