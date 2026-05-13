from policyengine_us.model_api import *


class ne_aabd_standard_of_need(Variable):
    value_type = float
    entity = Person
    label = "Nebraska AABD standard of need"
    unit = USD
    definition_period = MONTH
    defined_for = "ne_aabd_eligible"
    reference = (
        "https://dhhs.ne.gov/Documents/469-000-211.pdf",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ne.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.aabd
        living_arrangement = person("ne_aabd_living_arrangement", period)
        LA = living_arrangement.possible_values
        is_independent = living_arrangement == LA.INDEPENDENT
        couple_applies = person("ne_aabd_couple_rate_applies", period)
        # Per 469 NAC 3-006.02B1a / 3-006.02B3a(1)(a), the independent
        # budget is the standard of need plus actual shelter expense up to
        # the single (one person) or multiple (couple) shelter cap. Shelter
        # includes rent and home ownership expenses (469 NAC 3-004.02).
        independent_size = where(couple_applies, 2, 1)
        independent_son = p.standard_of_need.independent[independent_size]
        shelter_max = where(
            couple_applies,
            p.shelter_allowance.multiple,
            p.shelter_allowance.single,
        )
        actual_shelter = person.spm_unit("housing_cost", period)
        independent_shelter = min_(actual_shelter, shelter_max)
        independent_total = independent_son + independent_shelter
        # Couples split the combined budget 50/50 between spouses.
        independent_amount = where(
            couple_applies,
            independent_total / 2,
            independent_total,
        )
        # Alternate-living standards already include the $64 personal
        # needs allowance (except LONG_TERM_CARE, where Medicaid covers
        # personal needs and the standard is just $60). Per SSA 2011 PDF
        # p.2 footnote a, alternate-living couples are treated as two
        # individuals -- no pooling.
        alternate_amount = p.alternate_living_standard[living_arrangement]
        return where(is_independent, independent_amount, alternate_amount)
