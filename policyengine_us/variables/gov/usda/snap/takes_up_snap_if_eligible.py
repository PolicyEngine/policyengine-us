from policyengine_us.model_api import *


class takes_up_snap_if_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Whether an eligible SPM unit claims SNAP"
    documentation = (
        "Generated stochastically in the dataset using take-up rates. "
        "No formula - purely deterministic rules engine."
    )
    definition_period = YEAR
    # For policy calculator (non-dataset), defaults to True (full take-up assumption)
    default_value = True
