from openfisca_us.model_api import *


class spm_unit_state_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit state tax"
    definition_period = YEAR
    unit = USD
