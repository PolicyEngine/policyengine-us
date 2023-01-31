from policyengine_us.model_api import *


class non_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "non-refundable CTC"
    unit = USD
    documentation = (
        "The portion of the Child Tax Credit that is not refundable."
    )
    definition_period = YEAR
    adds = ["ctc"]
    subtracts = ["refundable_ctc"]
