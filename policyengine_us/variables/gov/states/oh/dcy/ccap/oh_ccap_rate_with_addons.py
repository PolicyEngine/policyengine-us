from policyengine_us.model_api import *


def ohio_rate_with_addons(person, period, parameters, step_up_to_quality):
    """The 5180:6-1-10 payment rate after its add-ons.

    The Child Care Choice Voucher passes step_up_to_quality=False: H.B. 96,
    Section 423.190, pays it the Publicly Funded Child Care rates without the
    Step Up To Quality enhancement, so paragraph (C) drops out and every rate
    that builds on "(B)(1) or (C)" builds on (B)(1).
    """
    # 5180:6-1-10(B)(1)-(2): the base rate for all add-ons is the lower
    # of the Appendix A county rate and the provider's customary charge.
    p = parameters(period).gov.states.oh.dcy.ccap.addons
    base_rate = person("oh_ccap_base_rate", period)
    customary_charge = person("pre_subsidy_childcare_expenses", period)
    capped_base = min_(base_rate, customary_charge)

    # (C)/(D): the higher of the Step Up To Quality bonus and the
    # accredited bonus is added on top of the (B)(1) base; this quality
    # payment may exceed the customary charge.
    quality_tier = person("oh_ccap_quality_tier", period)
    is_sutq = (quality_tier != quality_tier.possible_values.NONE) & step_up_to_quality
    sutq_pct = where(is_sutq, p.quality.sutq[quality_tier], 0)
    sutq_rate = capped_base * (1 + sutq_pct)
    is_accredited = person("oh_ccap_is_accredited", period)
    accredited_pct = where(is_accredited, p.accredited, 0)
    accredited_rate = capped_base * (1 + accredited_pct)
    rate_after_quality = max_(sutq_rate, accredited_rate)

    # (F)/(G) refer only to the rate established under (B)(1) or (C).
    # Accreditation under (D) is a separate payment and therefore is not
    # compounded by the non-traditional-hours or special-needs percentage.
    enhancement_base = where(is_sutq, sutq_rate, capped_base)

    non_traditional = person("oh_ccap_non_traditional_hours", period)
    non_traditional_pct = where(non_traditional, p.non_traditional_hours, 0)
    has_special_needs = person("oh_ccap_special_needs", period)
    has_accommodations = person("oh_ccap_has_special_accommodations", period)
    accommodations = has_special_needs & has_accommodations

    # (F)(1)/(G)(1): the non-traditional-hours and special-needs
    # percentages are computed on the (B)(1)-or-(C) rate; per (F)(3) and
    # (G)(1) these payments may not exceed the customary charge, and they
    # never reduce the (C) rate already established.
    percentage_add = non_traditional_pct + where(
        has_special_needs & ~accommodations, p.special_needs, 0
    )
    percentage_payment = rate_after_quality + enhancement_base * percentage_add
    capped_percentage_payment = max_(
        rate_after_quality,
        min_(percentage_payment, customary_charge),
    )
    # (G)(2): approved special accommodations double the (B)(1)-or-(C)
    # rate with no customary-charge cap (5180:2-16-09 approval). Any
    # accreditation payment remains separate, and any non-traditional
    # share stays additive.
    separate_accreditation_payment = rate_after_quality - enhancement_base
    accommodations_payment = (
        enhancement_base
        * (p.special_needs_accommodations_multiplier + non_traditional_pct)
        + separate_accreditation_payment
    )
    return where(accommodations, accommodations_payment, capped_percentage_payment)


class oh_ccap_rate_with_addons(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Ohio CCAP monthly maximum reimbursement rate after add-ons"
    definition_period = MONTH
    defined_for = "oh_ccap_eligible_child"
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-10",
        "https://codes.ohio.gov/assets/laws/administrative-code/authenticated/5180/2/16/5180$2-16-09_20231007.pdf",
    )

    def formula(person, period, parameters):
        return ohio_rate_with_addons(
            person, period, parameters, step_up_to_quality=True
        )
