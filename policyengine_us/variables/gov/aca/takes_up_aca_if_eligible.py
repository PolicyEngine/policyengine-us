from policyengine_us.model_api import *


class takes_up_aca_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether an eligible tax unit claims ACA Premium Tax Credit"
    documentation = (
        "Generated stochastically in the dataset using take-up rates. "
        "No formula - purely deterministic rules engine."
    )
    definition_period = YEAR
    # For policy calculator (non-dataset), defaults to True (full take-up assumption)
    default_value = True
