from openfisca_us.model_api import *


class spm_unit_capped_work_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit work and childcare expenses"
    definition_period = YEAR
    unit = USD
