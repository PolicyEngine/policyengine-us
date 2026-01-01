from policyengine_us.model_api import *
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

        # Per 7 AAC 45.525: Payment = (Need Standard - Countable Income)
        # * (Max Payment for 2 persons) / (Need Standard for 2 persons)
        is_child_only = spm_unit("ak_atap_is_child_only_unit", period)
        is_pregnant_only = spm_unit("ak_atap_is_pregnant_woman_only", period)

        # Reference values for size 2
        # Note: Parameter keys are strings when accessed at instant
        need_ref_child = p.income.need_standard.child_only.amount["2"]
        need_ref_adult = p.income.need_standard.adult_included.amount["2"]
        need_ref_pregnant = p.income.need_standard.pregnant_woman.amount

        # For adult-included: size 2 = 1 caretaker + 1 child = base only ($821)
        # For child-only: size 2 = 2 children = base + 1 additional ($554)
        payment_ref_child = (
            p.payment.child_only.base + p.payment.child_only.additional_child
        )
        payment_ref_adult = p.payment.one_caretaker.base
        payment_ref_pregnant = p.payment.pregnant_woman

        # Select appropriate reference values
        need_for_2 = where(
            is_pregnant_only,
            need_ref_pregnant,
            where(is_child_only, need_ref_child, need_ref_adult),
        )
        payment_for_2 = where(
            is_pregnant_only,
            payment_ref_pregnant,
            where(is_child_only, payment_ref_child, payment_ref_adult),
        )

        # Calculate benefit
        income_deficit = max_(need_standard - countable_income, 0)
        raw_payment = np.floor(income_deficit * payment_for_2 / need_for_2)

        # Minimum payment: $10 (payments below $10 are not issued)
        minimum = p.payment.minimum
        return where(raw_payment >= minimum, raw_payment, 0)
