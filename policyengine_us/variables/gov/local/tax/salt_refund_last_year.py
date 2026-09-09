from policyengine_us.model_api import *


class salt_refund_last_year(Variable):
    value_type = float
    entity = TaxUnit
    label = "SALT refund last year"
    unit = USD
    definition_period = YEAR
    documentation = (
        "[DEPRECATED] Use salt_refund_income instead. Taxable state and local"
        " tax refund income for the tax unit (Form 1040, Schedule 1, line 1 /"
        " IRC § 111)."
    )

    adds = ["salt_refund_income"]
