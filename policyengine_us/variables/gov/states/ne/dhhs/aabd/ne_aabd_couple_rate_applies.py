from policyengine_us.model_api import *


class ne_aabd_couple_rate_applies(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska AABD couple rate applies"
    definition_period = MONTH
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Documents/Title-469-Complete.pdf#page=130",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ne.pdf#page=2",
    )

    def formula(person, period):
        # Per 469 NAC 3-006.02B3a(1), an eligible AABD couple living
        # together independently uses a single combined budget split
        # 50/50. Per SSA 2011 PDF p.2 footnote a, alternate-living
        # couples are treated as two individuals -- so the couple
        # branch only fires when both spouses are in INDEPENDENT.
        # is_ssi_eligible is used (not ne_aabd_eligible) to avoid a
        # circular dependency on the benefit calculation.
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        unit_size = person.marital_unit.nb_persons()
        both_ssi_eligible = (
            person.marital_unit.sum(person("is_ssi_eligible", period.this_year))
            == unit_size
        )
        living_arrangement = person("ne_aabd_living_arrangement", period)
        LA = living_arrangement.possible_values
        is_independent = living_arrangement == LA.INDEPENDENT
        both_independent = person.marital_unit.sum(is_independent) == unit_size
        return joint_claim & both_ssi_eligible & both_independent
