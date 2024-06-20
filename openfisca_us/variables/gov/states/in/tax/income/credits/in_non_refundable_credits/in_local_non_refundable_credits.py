from openfisca_us.model_api import *


class in_local_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN non-refundable credits"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        [
            "in_local_taxes_paid_outside_state_credit",
            "in_other_local_nonrefundable_credits",
        ]
    )
