from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ak.dpa.atap.ak_atap_unit_type import (
    AKATAPUnitType,
)


class ak_atap_maximum_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP maximum payment"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.523",
        "https://www.akleg.gov/basis/statutes.asp#47.27.025",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.atap.payment
        unit_type = spm_unit("ak_atap_unit_type", period)

        # Count children for additional child calculation
        person = spm_unit.members
        is_child = person("is_child", period.this_year)
        num_children = spm_unit.sum(is_child)
        additional_children = max_(num_children - 1, 0)

        # Child-only: $452 base + $102 per additional child
        child_only_payment = (
            p.child_only.base
            + additional_children * p.child_only.additional_child
        )

        # Pregnant woman only: flat $514
        pregnant_payment = p.pregnant_woman

        # One caretaker: $821 base + $102 per additional child
        one_caretaker_payment = (
            p.one_caretaker.base
            + additional_children * p.one_caretaker.additional_child
        )

        # Two-parent with incapacitated parent: $923 base + $102 per additional child
        # $923 = $821 (one_caretaker base) + $102 (incapacitated add-on)
        incapacitated_payment = (
            p.one_caretaker.base
            + p.incapacitated_parent
            + additional_children * p.one_caretaker.additional_child
        )

        # Two-parent able-bodied: same as one caretaker but with summer reduction
        # Per State Plan: "During the months of July, August and September,
        # this amount is reduced by 50 percent."
        month = period.start.month
        is_summer = (month >= 7) & (month <= 9)
        summer_rate = p.two_parent_able.summer_reduction_rate
        two_parent_able_payment = where(
            is_summer,
            one_caretaker_payment * (1 - summer_rate),
            one_caretaker_payment,
        )

        return select(
            [
                unit_type == AKATAPUnitType.PREGNANT_WOMAN,
                unit_type == AKATAPUnitType.CHILD_ONLY,
                unit_type == AKATAPUnitType.TWO_PARENT_INCAPACITATED,
                unit_type == AKATAPUnitType.TWO_PARENT_ABLE,
            ],
            [
                pregnant_payment,
                child_only_payment,
                incapacitated_payment,
                two_parent_able_payment,
            ],
            default=one_caretaker_payment,
        )
