from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)


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
        expansion_fmap = p.expansion_fmap
        group = person("medicaid_group", period)
        is_expansion = group == MedicaidGroup.EXPANSION_ADULT
        return where(is_expansion, expansion_fmap, regular_fmap)
