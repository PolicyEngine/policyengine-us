from policyengine_us.model_api import *


class medicaid_federal_share(Variable):
    value_type = float
    entity = Person
    label = "Medicaid federal share (FMAP applicable to enrollee)"
    documentation = (
        "Federal medical assistance percentage applied to this enrollee's "
        "Medicaid expenditures. Uses the ACA expansion FMAP for expansion "
        "adults (42 U.S.C. 1396d(y)) and the state's regular FMAP for all "
        "other enrollment groups (42 U.S.C. 1396d(b))."
    )
    unit = "/1"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396d"
    defined_for = "medicaid_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.cost_share
        state = person.household("state_code", period)
        regular_fmap = p.fmap[state]
        category = person("medicaid_category", period)
        categories = category.possible_values
        return select(
            [
                category == categories.ADULT,
                category != categories.NONE,
            ],
            [p.expansion_fmap, regular_fmap],
            default=0,
        )
