from policyengine_us.model_api import *


class ak_atap_maximum_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP maximum payment"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.523"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.atap.payment
        unit_size = spm_unit("ak_atap_unit_size", period)
        is_child_only = spm_unit("ak_atap_is_child_only_unit", period)
        is_pregnant_only = spm_unit("ak_atap_is_pregnant_woman_only", period)

        # Count children for additional child calculation
        person = spm_unit.members
        is_child = person("is_child", period.this_year)
        num_children = spm_unit.sum(is_child)

        # Child-only: $452 base + $102 per additional child
        child_only_payment = p.child_only.base + (
            max_(num_children - 1, 0) * p.child_only.additional_child
        )

        # Pregnant woman only: flat $514
        pregnant_payment = p.pregnant_woman

        # One caretaker: $821 base + $102 per additional child
        one_caretaker_payment = p.one_caretaker.base + (
            max_(num_children - 1, 0) * p.one_caretaker.additional_child
        )

        return where(
            is_pregnant_only,
            pregnant_payment,
            where(is_child_only, child_only_payment, one_caretaker_payment),
        )
