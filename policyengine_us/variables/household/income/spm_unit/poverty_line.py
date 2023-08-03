from policyengine_us.model_api import *


class poverty_line(Variable):
    value_type = float
    entity = SPMUnit
    label = "poverty line"
    unit = USD
    documentation = "Income threshold below which a household is considered to be in poverty."
    definition_period = YEAR
    adds = [
        "spm_unit_spm_threshold",
    ]
