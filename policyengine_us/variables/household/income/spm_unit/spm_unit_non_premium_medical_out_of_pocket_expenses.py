from policyengine_us.model_api import *


class spm_unit_non_premium_medical_out_of_pocket_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit non-premium medical out-of-pocket expenses"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Non-premium medical out-of-pocket expenses for an SPM unit. Unlike "
        "the generic `medical_out_of_pocket_expenses` variable used by tax "
        "and benefit programs, the SPM definition includes over-the-counter "
        "health expenses."
    )

    adds = [
        "other_medical_expenses",
        "over_the_counter_health_expenses",
    ]
