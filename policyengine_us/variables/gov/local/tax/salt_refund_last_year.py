from policyengine_us.model_api import *


class salt_refund_last_year(Variable):
    value_type = float
    entity = TaxUnit
    label = "SALT refund last year"
    unit = USD
    documentation = "Total state and local tax refund income for the tax unit."
    definition_period = YEAR

    adds = ["salt_refund_income"]
