from policyengine_us.model_api import *


class simulated_aca_take_up_if_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether a tax unit is simulated to take up ACA if eligible"
    definition_period = YEAR
    default_value = True
    documentation = (
        "Data-supplied or reform-responsive Marketplace take-up switch for "
        "tax units without reported Marketplace coverage at interview. "
        "Population data should write this input rather than the formula-owned "
        "takes_up_aca_if_eligible variable."
    )
