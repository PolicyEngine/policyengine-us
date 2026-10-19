from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_established_spouse_indices,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    has_parent_ids,
    household_has_parent_ids,
    household_member_indices,
    unlinked_parent,
)


class ssi_spousal_deeming_child_allocations(Variable):
    value_type = float
    entity = Person
    label = "SSI ineligible child allocations from an ineligible spouse's income"
    documentation = (
        "The sum of the ineligible child allocations deducted from the "
        "income of this person's ineligible spouse before it is deemed: one "
        "for each ineligible child of this person or of their spouse who "
        "lives in their household. A child whose parent ids are set counts "
        "when an id names this person or their co-resident spouse. A child "
        "without ids counts when they belong to the tax unit of this person "
        "or of their spouse; in a household with parent links, only when "
        "this person or their spouse is a parent some of whose children no "
        "id names. Without ids, a grandchild or other relative in that tax "
        "unit cannot be told apart from a child, so supply parent ids. Enter "
        "a child who is only temporarily absent, such as a child away at "
        "school who is still under parental control, in the household they "
        "remain a member of (416.1167, POMS SI 01310.165)."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1160#p-416.1160(d)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501310115",
        "https://secure.ssa.gov/poms.nsf/lnx/0501310140",
    )

    def formula(person, period, parameters):
        allocation = person("ssi_ineligible_child_allocation", period)
        # 416.1160(d): 'your natural child or adopted child, or the natural
        # or adopted child of your spouse ... who lives in the same household
        # with you'. Its other clause, the child 'of your parent or of your
        # parent's spouse', serves parent-to-child deeming: POMS SI 01310.115
        # A.3 and SI 01310.140 A give spouse-to-spouse deeming the children of
        # either member of the couple. Parent ids resolve among household
        # members, so a child who lives elsewhere names no co-resident parent.
        first, second = co_resident_parent_indices(person, period)
        spouse = _ssi_established_spouse_indices(person, period, first, second)
        has_spouse = spouse >= 0
        safe_spouse = np.maximum(spouse, 0)
        own_index = np.arange(person.count)
        # Without ids, keep the tax-unit grouping, extended to a spouse who
        # files separately. In a household with links, the parent-link
        # contract lets this proxy assign a child only to unlinked parents.
        tax_unit = person.tax_unit.reference_entity.members_entity_id
        spouse_tax_unit = np.where(has_spouse, tax_unit[safe_spouse], -1)
        unlinked = unlinked_parent(person, period)
        may_presume = ~household_has_parent_ids(person, period) | (
            unlinked | (has_spouse & unlinked[safe_spouse])
        )
        linked_child = has_parent_ids(person, period)
        total = np.zeros(person.count)
        for child in household_member_indices(person):
            safe = np.maximum(child, 0)
            named = (first[safe] == own_index) | (second[safe] == own_index)
            named_spouse = has_spouse & (
                (first[safe] == spouse) | (second[safe] == spouse)
            )
            presumed = may_presume & (
                (tax_unit[safe] == tax_unit) | (tax_unit[safe] == spouse_tax_unit)
            )
            counts = (
                (child >= 0)
                & (child != own_index)
                & (child != spouse)
                & where(linked_child[safe], named | named_spouse, presumed)
            )
            total += where(counts, allocation[safe], 0)
        return total
