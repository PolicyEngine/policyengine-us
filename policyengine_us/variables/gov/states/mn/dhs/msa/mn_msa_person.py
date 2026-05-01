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
        # Per Minn. Stat. § 256D.44 Subd. 1 and SSA 2011 baseline:
        # for SSI-track recipients the federal SSI payment is deducted
        # from the (combined federal+state) assistance standard, leaving
        # the state portion. For non-SSI excess-income recipients there
        # is no federal SSI deduction. Countable income further reduces
        # the state benefit. Special-needs allowances add on top of the
        # assistance-standard-derived base.
        # The COUPLE_* assistance standards are couple totals, so split
        # them 50/50 across the two eligible spouses.
        # ssi is YEAR-defined with USD units, so accessing it from this
        # MONTH formula auto-divides by 12.
        arrangement = person("mn_msa_living_arrangement", period)
        LA = arrangement.possible_values
        is_couple_arrangement = (arrangement == LA.COUPLE_LIVING_ALONE) | (
            arrangement == LA.COUPLE_LIVING_WITH_OTHERS
        )
        standard = person("mn_msa_assistance_standard", period)
        per_person_standard = where(is_couple_arrangement, standard / 2, standard)
        countable_income = person("mn_msa_countable_income", period)
        federal_ssi = person("ssi", period)
        receives_ssi = federal_ssi > 0
        ssi_track = max_(0, per_person_standard - federal_ssi - countable_income)
        non_ssi_track = max_(0, per_person_standard - countable_income)
        base = where(receives_ssi, ssi_track, non_ssi_track)
        special_needs = person("mn_msa_special_needs_total", period)
        return base + special_needs
