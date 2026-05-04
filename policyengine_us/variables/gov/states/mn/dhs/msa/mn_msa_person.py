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
        # Per Minn. Stat. § 256D.44 Subd. 1 and House Research (Oct 2024) p.3:
        # for SSI-track recipients, the county counts the federal SSI grant as
        # gross unearned income and then allows for a $20 general income
        # disregard against the combined (federal SSI + other unearned). The
        # federal SSI calculation already absorbed earned disregards, so MSA
        # does not re-apply $65 + 1/2 to earned for the SSI track.
        # For non-SSI excess-income recipients, there is no federal SSI; the
        # countable_income variable applies the $20 + $65 + 1/2 disregards
        # following the federal SSI methodology.
        # The COUPLE_* assistance standards are couple totals, so split them
        # 50/50 across the two eligible spouses. ssi is YEAR-defined with USD
        # units, so accessing it from this MONTH formula auto-divides by 12.
        # Empirical anchor: SSA 2011 Table 1 living-alone individual reports
        # state portion = $81 = $735 standard - max($674 SSI - $20, 0).
        arrangement = person("mn_msa_payment_category", period)
        LA = arrangement.possible_values
        is_couple_arrangement = (arrangement == LA.COUPLE_LIVING_ALONE) | (
            arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )
        standard = person("mn_msa_assistance_standard", period)
        per_person_standard = where(is_couple_arrangement, standard / 2, standard)
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
        # The $20 disregard applies to FLA-A (living alone) and FLA-B (with
        # others) recipients but NOT to FLA-D (Medicaid facility) recipients,
        # whose $30 federal SSI is a strict personal-needs cap. SSA 2011
        # Table 1: Medicaid-facility individual state portion = $59 = $89 -
        # $30 with no $20 added back.
        is_medicaid_facility = arrangement == LA.MEDICAID_FACILITY
        disregard = where(is_medicaid_facility, 0, p.general)
        # For couples, the $20 disregard is applied once to combined couple
        # income; allocate half to each spouse so the per-person formulas sum
        # to the correct couple total.
        per_person_disregard = where(is_couple_arrangement, disregard / 2, disregard)
        ssi_track_countable = max_(ssi_fbr + raw_unearned - per_person_disregard, 0)
        ssi_track = max_(0, per_person_standard - ssi_track_countable)
        countable_income = person("mn_msa_countable_income", period)
        non_ssi_track = max_(0, per_person_standard - countable_income)
        base = where(receives_ssi, ssi_track, non_ssi_track)
        special_needs = person("mn_msa_special_needs_total", period)
        return base + special_needs
