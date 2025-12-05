from policyengine_us.model_api import *


class takes_up_medicaid_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Whether an eligible person enrolls in Medicaid"
    documentation = (
        "Generated stochastically in the dataset using take-up rates. "
        "No formula - purely deterministic rules engine."
    )
    definition_period = YEAR
    # For policy calculator (non-dataset), defaults to True (full take-up assumption)
    default_value = True
