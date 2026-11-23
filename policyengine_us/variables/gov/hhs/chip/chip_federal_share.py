from policyengine_us.model_api import *


class chip_federal_share(Variable):
    value_type = float
    entity = Person
    label = "CHIP federal share (enhanced FMAP)"
    documentation = (
        "Enhanced federal medical assistance percentage (eFMAP) applied to "
        "CHIP expenditures: regular state FMAP plus 30 percent of the gap "
        "between regular FMAP and 100 percent, capped at 85 percent "
        "(42 U.S.C. 1397ee(b)(1)). An undocumented child whom CHIP enrolls in "
        "its child category through the route that "
        "gov.hhs.chip.undocumented.child opens gets no federal share "
        "(8 U.S.C. 1611). An undocumented child whom New Jersey's "
        "all-children route admits keeps the match here."
    )
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1397ee#b",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title8/html/USCODE-2024-title8-chap14-subchapI-sec1611.htm",
    )
    defined_for = "chip_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs
        fmap = p.medicaid.cost_share.fmap
        state = person.household("state_code", period)
        regular_fmap = fmap[state]
        efmap = min_(regular_fmap + 0.30 * (1 - regular_fmap), 0.85)
        # 8 U.S.C. 1611 bars federal payment for a child with no federal
        # immigration route. The state alone funds an undocumented child whom
        # CHIP enrolls in its child category through the route that
        # gov.hhs.chip.undocumented.child opens, so that child gets no match.
        # This formula does not apply that to other state routes: an
        # undocumented child whom New Jersey admits through
        # regardless_of_immigration_status.child_age_limit keeps the match.
        # The unborn-child route tests no immigration status and keeps its
        # match.
        status = person("immigration_status", period)
        state_str = person.household("state_code_str", period)
        category = person("chip_category", period)
        state_funded_child = (
            (category == category.possible_values.CHILD)
            & (status == status.possible_values.UNDOCUMENTED)
            & p.chip.undocumented.child[state_str].astype(bool)
            & ~person("is_federal_chip_immigration_status_eligible", period)
        )
        return where(state_funded_child, 0, where(regular_fmap > 0, efmap, 0))
