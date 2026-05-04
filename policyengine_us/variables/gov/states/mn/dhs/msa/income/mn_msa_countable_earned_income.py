from policyengine_us.model_api import *


class mn_msa_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid countable earned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=2",
    )

    def formula(person, period, parameters):
        # SSI-track recipients already have $20 + $65 + 1/2 disregards
        # consumed inside ssi_countable_income, so MSA earned is treated
        # as fully disregarded to avoid double-counting.
        gross_earned = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        disregard = person("mn_msa_earned_income_disregard", period)
        arrangement = person("mn_msa_payment_category", period)
        LA = arrangement.possible_values
        is_couple = (arrangement == LA.COUPLE_LIVING_ALONE) | (
            arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )
        # Couples: aggregate gross earned and disregard at marital unit,
        # then split countable 50/50 — prevents wasting the disregard
        # when one spouse has zero earnings.
        couple_countable = (
            max_(
                person.marital_unit.sum(gross_earned)
                - person.marital_unit.sum(disregard),
                0,
            )
            / 2
        )
        individual_countable = max_(gross_earned - disregard, 0)
        non_ssi_track_countable = where(
            is_couple, couple_countable, individual_countable
        )
        receives_ssi = person("ssi", period) > 0
        return where(receives_ssi, 0, non_ssi_track_countable)
