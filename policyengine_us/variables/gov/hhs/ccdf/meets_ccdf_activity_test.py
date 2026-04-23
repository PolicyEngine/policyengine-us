from policyengine_us.model_api import *


class meets_ccdf_activity_test(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    documentation = (
        "Indicates whether parent or parents meet activity test "
        "(working/in job training/in educational program). "
        "Use this input to cover approved activities not individually "
        "modeled in PolicyEngine, such as job search, education/training "
        "programs, SNAP E&T, VIEW participation, CPS referral, or "
        "temporary leave from work or school."
    )
    label = "Activity test for CCDF"
