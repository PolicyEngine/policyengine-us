from policyengine_us.model_api import *


class ca_state_supplement_food_allowance(Variable):
    value_type = float
    entity = SPMUnit
    label = "California SSI state supplement food allowance"
    unit = USD
    definition_period = MONTH
    defined_for = "ca_state_supplement_food_allowance_eligible"
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415058",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.cdss.state_supplement.payment_standard
        is_married = spm_unit("spm_unit_is_married", period)
        aged_disabled_count = spm_unit(
            "ca_state_supplement_aged_disabled_count", period
        )
        # Food allowance amount
        allowance = where(
            is_married & (aged_disabled_count == 2),
            p.allowance.food.married,
            p.allowance.food.single,
        )
        # WIC 12200(e) adds the allowance only to the aged or disabled amount
        # under (c) or (d), not to the blind amounts under (a) or (b), and
        # California pays the highest category (POMS SI 01415.058 B.2.a note).
        # So the allowance counts only as far as it lifts the aged or disabled
        # amount above the blind amount; a couple of an aged person and a blind
        # person who is neither aged nor disabled gets none. POMS code C adds
        # the individual allowance for that couple; PolicyEngine follows the
        # statute (ruled 2026-10-29, PR 10379 comment 6509402355).
        aged_disabled_amount = spm_unit(
            "ca_state_supplement_aged_disabled_amount", period
        )
        blind_amount = spm_unit("ca_state_supplement_blind_amount", period)
        return max_(
            aged_disabled_amount + allowance - max_(blind_amount, aged_disabled_amount),
            0,
        )
