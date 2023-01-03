from policyengine_us.model_api import *


class il_final_taxation_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Il Final Taxation Amount"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL

    adds = ["il_total_tax"]
    subtracts = ["il_total_payments_and_refundable_credit"]
