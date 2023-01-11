from policyengine_us.model_api import *


class ctc_maximum_with_arpa_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum CTC for ARPA"
    unit = USD
    documentation = (
        "Maximum value of the Child Tax Credit, before phase-out, under ARPA."
    )
    definition_period = YEAR

    adds = ["ctc_maximum", "ctc_arpa_addition"]
