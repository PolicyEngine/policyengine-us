from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deeming import (
    ssi_ineligible_parents,
)


class is_ssi_ineligible_parent(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-ineligible parent in respect of a child"
    documentation = (
        "Whether this person is an ineligible parent of a co-resident child "
        "to whom SSI parental income deeming applies: the child's natural, "
        "adoptive or step parent, or the co-resident spouse of one, who does "
        "not meet the SSI status conditions."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1160#p-416.1160(d)",
        "https://www.ecfr.gov/current/title-20/section-416.1165",
    )

    def formula(person, period, parameters):
        rows, ineligible, _ = ssi_ineligible_parents(person, period)
        applies = person("is_ssi_income_deeming_child", period)
        deemors = rows[applies[:, None] & ineligible]
        return np.isin(np.arange(person.count), deemors)
