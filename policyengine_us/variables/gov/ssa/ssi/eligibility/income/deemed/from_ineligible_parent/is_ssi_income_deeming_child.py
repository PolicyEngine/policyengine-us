from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deeming import (
    ssi_ineligible_parents,
    ssi_parental_deeming_child,
)


class is_ssi_income_deeming_child(Variable):
    value_type = bool
    entity = Person
    label = "Child subject to parental SSI income deeming"
    documentation = (
        "An eligible child to whom SSI deems an ineligible parent's income: "
        "under 18, not married, not the head of a household, aged, blind or "
        "disabled and a citizen or qualified noncitizen, and living with at "
        "least one ineligible parent. An ineligible parent is a natural, "
        "adoptive or step parent named by the child's parent ids, or the "
        "co-resident spouse of one, who does not meet the SSI status "
        "conditions; without ids, an unlinked parent in the child's tax unit "
        "or the spouse of one stands in."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1165",
        "https://www.ecfr.gov/current/title-20/section-416.1160#p-416.1160(d)",
        "https://www.ecfr.gov/current/title-20/section-416.1856",
        "https://secure.ssa.gov/poms.nsf/lnx/0501310115",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320500",
    )

    def formula(person, period, parameters):
        _, ineligible, _ = ssi_ineligible_parents(person, period)
        return ssi_parental_deeming_child(person, period, ineligible)
