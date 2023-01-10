from policyengine_us.model_api import *


class spm_unit_self_employment_tax(Variable):
    value_type = float
    entity = SPMUnit
    label = "Self employment tax"
    definition_period = YEAR
    unit = USD

    adds = ["self_employment_tax"]
