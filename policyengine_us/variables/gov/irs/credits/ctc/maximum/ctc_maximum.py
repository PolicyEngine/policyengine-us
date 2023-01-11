from policyengine_us.model_api import *


class ctc_maximum(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maximum CTC"
    unit = USD
    documentation = "Maximum value of the Child Tax Credit, before phase-out."
    definition_period = YEAR

    adds = ["ctc_individual_maximum"]
