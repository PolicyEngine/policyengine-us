from policyengine_us.model_api import *


class il_final_taxation_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Il Final Taxation Amount"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        return tax_unit("il_total_tax", period) - tax_unit(
            "il_total_payments_and_refundable_credit", period
        )
