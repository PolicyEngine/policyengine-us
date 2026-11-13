from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class medicaid_federal_share(Variable):
    value_type = float
    entity = Person
    label = "Medicaid federal share (FMAP applicable to enrollee)"
    documentation = (
        "Federal medical assistance percentage applied to this enrollee's "
        "Medicaid expenditures. Uses the ACA expansion FMAP (42 U.S.C. "
        "1396d(y), and 1396d(z)(2) for childless adults in pre-ACA expansion "
        "states) for adult-category enrollees with income at or below 133 "
        "percent of the poverty line plus the 5 percentage point disregard, "
        "in a state whose adult income limit reaches that level (CMS does "
        "not match a partial expansion at the enhanced rate). Adults in a "
        "state with a lower adult limit (such as Wisconsin's childless adults "
        "to 100 percent of the poverty line) and adults above that level in "
        "a state with a higher limit receive the state's regular FMAP (42 "
        "U.S.C. 1396d(b)), as do all other enrollment groups. In a state "
        "with a higher adult group, 42 CFR 435.603(d)(4) gives the disregard "
        "to that group, so adults between 133 and 138 percent of the poverty "
        "line there are also in it at the regular FMAP; that band is not "
        "modeled. Rhode Island's "
        "postpartum continuation receives no Title XIX match unless the "
        "pregnancy was covered by Medicaid and the enrollee meets Medicaid "
        "immigration requirements: RIte Start serves people not eligible "
        "under Title XIX or XXI, and CHIP and FCEP pregnancies are Title XXI "
        "coverage. An enrollee who also meets a federally matched group keeps "
        "that group's match. Separate Title XXI health services "
        "initiative funding is not included here."
    )
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396d",
        "https://www.law.cornell.edu/uscode/text/42/1396a#a_10_A_i_VIII",
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm",
        "https://www.medicaid.gov/medicaid/spa/downloads/RI-22-0024.pdf#page=7",
        "https://www.medicaid.gov/CHIP/Downloads/RI-22-0026.pdf#page=2",
    )
    defined_for = "medicaid_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.cost_share
        state = person.household("state_code", period)
        regular_fmap = p.fmap[state]
        category = person("medicaid_category", period)
        categories = category.possible_values
        federally_matched_route = (category != categories.NONE) & person(
            "is_medicaid_immigration_status_eligible", period
        )
        no_federal_medicaid_match = (
            person("ri_medicaid_state_funded_postpartum_eligible", period)
            & ~federally_matched_route
        )
        # The expansion FMAP covers only the subclause (VIII) adult group.
        # Adults above the group limit in a state with a higher one are
        # covered through an optional group at the regular FMAP. CMS also
        # requires a state to cover adults to the full group limit: adults in
        # a state with a lower limit are covered through a section 1115
        # demonstration at the regular FMAP. The group limit includes the 5
        # percentage point MAGI disregard in every state. Where a higher
        # optional adult group exists, 42 CFR 435.603(d)(4) applies the
        # disregard to that group instead, which this does not model.
        adult_limit = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.adult.income_limit[state]
        group_limit = p.expansion_fmap_income_limit
        state_qualifies = where(
            p.expansion_fmap_requires_full_adult_group,
            adult_limit >= group_limit,
            True,
        )
        within_adult_group_limit = medicaid_income_eligible(
            person, period, parameters, group_limit
        )
        expansion_adult = (
            (category == categories.ADULT) & state_qualifies & within_adult_group_limit
        )
        return select(
            [
                no_federal_medicaid_match,
                expansion_adult,
                category != categories.NONE,
            ],
            [0, p.expansion_fmap, regular_fmap],
            default=0,
        )
