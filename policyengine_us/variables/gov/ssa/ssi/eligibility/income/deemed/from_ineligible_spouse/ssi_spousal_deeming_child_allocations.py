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
        "for each ineligible child who lives in their household and is the "
        "child of this person, of their spouse, of this person's parent or "
        "of that parent's spouse (416.1160(d)). A child whose parent ids are "
        "set counts when an id names this person or their co-resident "
        "spouse. For a person with a co-resident spouse, such a child also "
        "counts when one of the child's ids equals one of this person's own "
        "parent ids (a sibling or half-sibling, wherever that parent lives), "
        "or names the co-resident spouse of this person's co-resident parent "
        "(a step-sibling). An id for a parent outside the simulation must "
        "name that parent alone, and each of that parent's children must "
        "carry it. A child without ids counts when they belong to the tax "
        "unit of this person or of their spouse; in a household with parent "
        "links, only when this person or their spouse is a parent some of "
        "whose children no id names. Without ids, a grandchild or other "
        "relative in that tax unit cannot be told apart from a child, and a "
        "sibling in another tax unit cannot be found, so supply parent ids. "
        "Enter a child who is only temporarily absent, such as a child away "
        "at school who is still under parental control, in the household "
        "they remain a member of (416.1167, POMS SI 01310.165)."
    )
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.ecfr.gov/current/title-20/section-416.1163#p-416.1163(b)",
        "https://www.ecfr.gov/current/title-20/section-416.1160#p-416.1160(d)",
        "https://www.ecfr.gov/current/title-20/section-416.1160#p-416.1160(c)(2)",
        "https://www.ecfr.gov/current/title-20/section-416.1101",
        "https://www.ecfr.gov/current/title-20/section-416.1132#p-416.1132(a)",
        "https://secure.ssa.gov/poms.nsf/lnx/0501310115",
        "https://secure.ssa.gov/poms.nsf/lnx/0501310140",
    )

    def formula(person, period, parameters):
        allocation = person("ssi_ineligible_child_allocation_monthly", period)
        # In 416.1160(d), SSA defines an ineligible child as a co-resident
        # child, not eligible for SSI, of you, of your spouse, or 'of your
        # parent or of your parent's spouse'. SSA applies that one definition
        # to spouse deemors (416.1160(c)(2), 416.1163(b)); 'you' is the
        # claimant (416.1101) and a household is a place of residence
        # (416.1132(a)). So the claimant's co-resident siblings, half-siblings
        # and step-siblings count, and the spouse's siblings do not. POMS
        # SI 01310.140 A lists only the couple's children; this formula
        # follows the regulation. Parent ids resolve among household members,
        # so a child who lives elsewhere names no co-resident parent.
        first, second = co_resident_parent_indices(person, period)
        spouse = _ssi_established_spouse_indices(person, period, first, second)
        has_spouse = spouse >= 0
        safe_spouse = np.maximum(spouse, 0)
        own_index = np.arange(person.count)
        # A sibling carries one of this person's own parent ids, wherever
        # that parent lives. A step-sibling's id names the co-resident spouse
        # of this person's co-resident parent.
        parent_1 = person("parent_1_id", period)
        parent_2 = person("parent_2_id", period)
        parent_spouses = [
            np.where(slot >= 0, spouse[np.maximum(slot, 0)], -1)
            for slot in (first, second)
        ]
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
            shares_parent = np.zeros(person.count, dtype=bool)
            for child_id in (parent_1[safe], parent_2[safe]):
                shares_parent |= (child_id != 0) & (
                    (child_id == parent_1) | (child_id == parent_2)
                )
            names_parent_spouse = np.zeros(person.count, dtype=bool)
            for child_parent in (first[safe], second[safe]):
                for parent_spouse in parent_spouses:
                    names_parent_spouse |= (child_parent >= 0) & (
                        child_parent == parent_spouse
                    )
            # Only a person with a co-resident spouse has income deemed, so
            # only that person's total takes their siblings.
            sibling = has_spouse & (shares_parent | names_parent_spouse)
            presumed = may_presume & (
                (tax_unit[safe] == tax_unit) | (tax_unit[safe] == spouse_tax_unit)
            )
            counts = (
                (child >= 0)
                & (child != own_index)
                & (child != spouse)
                & where(linked_child[safe], named | named_spouse | sibling, presumed)
            )
            total += where(counts, allocation[safe], 0)
        return total
