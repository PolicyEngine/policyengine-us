from openfisca_us.model_api import *


class spm_unit_total_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit total income"
    definition_period = YEAR
    unit = USD
