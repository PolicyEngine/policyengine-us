from policyengine_us.model_api import *


class meets_ccdf_activity_test(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = "Indicates whether parent or parents meet activity test (working/in job training/in educational program)"
    label = "Activity test for CCDF"
