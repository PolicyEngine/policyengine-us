from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ak.dpa.atap.ak_atap_unit_type import (
    AKATAPUnitType,
)
import numpy as np


class ak_atap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP benefit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.525",
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.523",
    )
    defined_for = "ak_atap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ak.dpa.atap
        need_standard = spm_unit("ak_atap_need_standard", period)
        countable_income = spm_unit("ak_atap_countable_income", period)
        maximum_payment = spm_unit("ak_atap_maximum_payment", period)
        unit_type = spm_unit("ak_atap_unit_type", period)

        # Per 7 AAC 45.525: Payment = (Need Standard - Countable Income)
        # * (Max Payment for ref size) / (Need Standard for ref size)

        # Reference values for need standard by unit type
        # Note: Parameter keys are strings when accessed at instant
        need_ref_child = p.income.need_standard.child_only.amount["2"]
        need_ref_adult = p.income.need_standard.adult_included.amount["2"]
        need_ref_pregnant = p.income.need_standard.pregnant_woman.amount
        # Incapacitated: min size is 3 (2 parents + 1 child)
        need_ref_incap = p.income.need_standard.incapacitated_parent.amount[
            "3"
        ]

        # Reference values for max payment by unit type
        # For child-only: size 2 = 2 children = base + 1 additional ($554)
        payment_ref_child = (
            p.payment.child_only.base + p.payment.child_only.additional_child
        )
        # For adult-included: size 2 = 1 caretaker + 1 child = base only ($821)
        payment_ref_adult = p.payment.one_caretaker.base
        payment_ref_pregnant = p.payment.pregnant_woman
        # For incapacitated: size 3 = 2 parents + 1 child = $923 base
        payment_ref_incap = (
            p.payment.one_caretaker.base + p.payment.incapacitated_parent
        )

        # Select appropriate reference values based on unit type
        need_for_ref = select(
            [
                unit_type == AKATAPUnitType.PREGNANT_WOMAN,
                unit_type == AKATAPUnitType.CHILD_ONLY,
                unit_type == AKATAPUnitType.TWO_PARENT_INCAPACITATED,
            ],
            [
                need_ref_pregnant,
                need_ref_child,
                need_ref_incap,
            ],
            default=need_ref_adult,
        )

        payment_for_ref = select(
            [
                unit_type == AKATAPUnitType.PREGNANT_WOMAN,
                unit_type == AKATAPUnitType.CHILD_ONLY,
                unit_type == AKATAPUnitType.TWO_PARENT_INCAPACITATED,
            ],
            [
                payment_ref_pregnant,
                payment_ref_child,
                payment_ref_incap,
            ],
            default=payment_ref_adult,
        )

        # Calculate benefit
        income_deficit = max_(need_standard - countable_income, 0)
        raw_payment = np.floor(income_deficit * payment_for_ref / need_for_ref)

        # Cap at maximum payment (important for two-parent summer reduction)
        capped_payment = min_(raw_payment, maximum_payment)

        # Minimum payment: $10 (payments below $10 are not issued)
        minimum = p.payment.minimum
        return where(capped_payment >= minimum, capped_payment, 0)
