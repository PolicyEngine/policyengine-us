from policyengine_us.model_api import *


class mn_msa_person(Variable):
    value_type = float
    entity = Person
    label = "Minnesota Supplemental Aid per-person amount"
    unit = USD
    definition_period = MONTH
    defined_for = "mn_msa_eligible_person"
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256D.44",
        "https://www.house.mn.gov/hrd/pubs/pap_MSA.pdf#page=2",
        "https://www.dhs.state.mn.us/main/groups/county_access/documents/pub/mndhs-073585.pdf#page=4",
    )

    def formula(person, period, parameters):
        # SSI track counts federal SSI FBR as gross unearned, then applies
        # the $20 general disregard. FLA-D (Medicaid facility) is exempt
        # from the $20 disregard. Non-SSI track uses mn_msa_countable_income
        # (already aggregates $20 + $65 + 1/2 federally).
        # Couples are computed at the marital unit then split 50/50.
        arrangement = person("mn_msa_payment_category", period)
        LA = arrangement.possible_values
        is_couple = (arrangement == LA.COUPLE_LIVING_ALONE) | (
            arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )
        is_medicaid_facility = arrangement == LA.MEDICAID_FACILITY
        standard = person("mn_msa_assistance_standard", period)
        ssi = person("ssi", period)
        receives_ssi = ssi > 0
        ssi_fbr = person("ssi_amount_if_eligible", period)
        p = parameters(period).gov.states.mn.dhs.msa.disregard
        raw_unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
                "ssi_unearned_income_deemed_from_ineligible_parent",
            ],
        )
        disregard = where(is_medicaid_facility, 0, p.general)

        # SSI track: aggregate FBR + unearned at marital unit for couples,
        # apply $20 once, then split supplement 50/50.
        couple_ssi_countable = max_(
            person.marital_unit.sum(ssi_fbr)
            + person.marital_unit.sum(raw_unearned)
            - disregard,
            0,
        )
        couple_ssi_supplement = max_(standard - couple_ssi_countable, 0) / 2
        individual_ssi_countable = max_(ssi_fbr + raw_unearned - disregard, 0)
        individual_ssi_supplement = max_(standard - individual_ssi_countable, 0)
        ssi_track = where(is_couple, couple_ssi_supplement, individual_ssi_supplement)

        # Non-SSI track: countable_income is already per-spouse share for
        # couples; sum across the marital unit gives the couple total.
        countable_income = person("mn_msa_countable_income", period)
        couple_non_ssi_supplement = (
            max_(standard - person.marital_unit.sum(countable_income), 0) / 2
        )
        individual_non_ssi_supplement = max_(standard - countable_income, 0)
        non_ssi_track = where(
            is_couple, couple_non_ssi_supplement, individual_non_ssi_supplement
        )

        base = where(receives_ssi, ssi_track, non_ssi_track)
        special_needs = person("mn_msa_special_needs_total", period)
        return base + special_needs
