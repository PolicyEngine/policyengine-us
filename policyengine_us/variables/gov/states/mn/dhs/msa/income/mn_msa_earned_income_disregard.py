from policyengine_us.model_api import *


class mn_msa_earned_income_disregard(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid earned income disregard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mn.dhs.msa.disregard
        gross_unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_parent",
            ],
        )
        gross_earned = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        arrangement = person("mn_msa_payment_category", period)
        LA = arrangement.possible_values
        is_couple = (arrangement == LA.COUPLE_LIVING_ALONE) | (
            arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )
        # Couples: aggregate to marital unit, apply $20 + $65 + 1/2 once,
        # then split 50/50 across spouses.
        couple_unearned = person.marital_unit.sum(gross_unearned)
        couple_earned = person.marital_unit.sum(gross_earned)
        couple_leftover = max_(p.general - couple_unearned, 0)
        couple_flat = p.earned.initial + couple_leftover
        couple_flat_disregard = min_(couple_earned, couple_flat)
        couple_remainder = max_(couple_earned - couple_flat, 0)
        couple_per_spouse = (
            couple_flat_disregard + couple_remainder * p.earned.rate
        ) / 2
        individual_leftover = max_(p.general - gross_unearned, 0)
        individual_flat = p.earned.initial + individual_leftover
        individual_flat_disregard = min_(gross_earned, individual_flat)
        individual_remainder = max_(gross_earned - individual_flat, 0)
        individual_disregard = (
            individual_flat_disregard + individual_remainder * p.earned.rate
        )
        return where(is_couple, couple_per_spouse, individual_disregard)
