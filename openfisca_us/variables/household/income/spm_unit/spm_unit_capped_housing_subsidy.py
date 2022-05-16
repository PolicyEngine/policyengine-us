from openfisca_us.model_api import *


class spm_unit_capped_housing_subsidy_reported(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit capped housing subsidy"
    definition_period = YEAR
    unit = USD
