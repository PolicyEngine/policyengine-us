from policyengine_us.model_api import *


class chip_federal_share(Variable):
    value_type = float
    entity = Person
    label = "CHIP federal share (enhanced FMAP)"
    documentation = (
        "Enhanced federal medical assistance percentage (eFMAP) applied to "
        "CHIP expenditures: regular state FMAP plus 30 percent of the gap "
        "between regular FMAP and 100 percent, capped at 85 percent "
        "(42 U.S.C. 1397ee(b)(1))."
    )
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1397ee#b"
    defined_for = "chip_enrolled"

    def formula(person, period, parameters):
        fmap = parameters(period).gov.hhs.medicaid.cost_share.fmap
        state = person.household("state_code", period)
        regular_fmap = fmap[state]
        efmap = min_(regular_fmap + 0.30 * (1 - regular_fmap), 0.85)
        return where(regular_fmap > 0, efmap, 0)
