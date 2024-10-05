from policyengine_us.model_api import *


class spm_unit_school_lunch_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit school lunch subsidy"
    definition_period = YEAR
    unit = USD
