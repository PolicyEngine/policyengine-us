from policyengine_us.model_api import *


class spm_unit_pre_subsidy_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit pre subsidy child care expenses"
    definition_period = YEAR
    unit = USD
