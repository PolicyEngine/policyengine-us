from openfisca_us.model_api import *


class in_state_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN non-refundable credits"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        [
            "in_other_non_refundable_credits",
            "in_college_credit",
            "in_taxes_paid_to_other_states_credit",
        ]
    )
