from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.deemed.from_ineligible_parent._ssi_parental_deeming import (
    ssi_ineligible_parents,
    ssi_parental_deeming_child_allocation_total,
)


class ssi_parental_deeming_child_allocations(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible child allocations from an ineligible parent's income"
    documentation = (
        "The sum of the ineligible child allocations deducted from the income "
        "of this person's ineligible parents before it is deemed to them: one "
        "for each ineligible child in their household who is their own child "
        "or a child of one of their parents or parents' spouses, that is, "
        "their siblings, half-siblings and step-siblings. A child whose "
        "parent ids are set counts when an id names this person or one of "
        "those parents. A child without ids counts when they belong to the "
        "tax unit of this person or of one of those parents; in a household "
        "with parent links, only when one of them is a parent some of whose "
        "children no id names. Without ids, a cousin or other relative in that "
        "tax unit cannot be told apart from a sibling, so supply parent ids."
    )
    unit = USD
    definition_period = YEAR
    defined_for = "is_ssi_income_deeming_child"
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1165#p-416.1165(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1160#p-416.1160(d)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501310115",
        "https://secure.ssa.gov/poms.nsf/lnx/0501310140",
        "https://secure.ssa.gov/poms.nsf/lnx/0501320500",
    )

    def formula(person, period, parameters):
        rows, _, _ = ssi_ineligible_parents(person, period)
        return ssi_parental_deeming_child_allocation_total(person, period, rows)
