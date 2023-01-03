from policyengine_us.model_api import *


class il_total_payments_and_refundable_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Il Total Payments And Refundable Credit"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.IL

    formula = sum_of_variables(
        [
            "il_pass_through_withholding",
            "il_pass_through_entity_tax_credit",
            "il_eitc",
        ]
    )
