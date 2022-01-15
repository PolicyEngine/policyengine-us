from openfisca_us.model_api import *


class spm_unit_wic(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit WIC subsidy"
    definition_period = YEAR
    unit = USD
