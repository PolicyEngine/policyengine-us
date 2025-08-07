from policyengine_us.model_api import *


class foreign_tax_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Foreign tax credit credit limit"
    definition_period = YEAR
    documentation = "Foreign tax credit from Form 1116"
    unit = USD

    # The foreign tax credit is the first non-refundable credit in Schedule 3 (Form 1040)
    adds = ["income_tax_before_credits"]
