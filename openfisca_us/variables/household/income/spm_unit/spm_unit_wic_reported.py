from openfisca_us.model_api import *


class spm_unit_wic_reported(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit WIC"
    definition_period = YEAR
    unit = USD
