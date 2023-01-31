from policyengine_us.model_api import *


class k12_tuition_and_fees(Variable):
    value_type = float
    entity = TaxUnit
    label = "K-12 Tuition and fees (from Form 8917)"
    unit = USD
    definition_period = YEAR
