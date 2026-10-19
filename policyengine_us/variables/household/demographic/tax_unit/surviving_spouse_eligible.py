from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    tax_unit_parent_indices,
)


class surviving_spouse_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Qualifies for surviving spouse filing status"
    documentation = (
        "IRC 2(a)(1)(B) requires a dependent son, stepson, daughter or "
        "stepdaughter, with dependency determined without regard to IRC "
        "152(b)(1), (b)(2) and (d)(1)(B). The qualifying relative gross "
        "income test of 152(d)(1)(B) does not apply, so an adult child with "
        "gross income at or above the exemption amount still qualifies the "
        "filer. Each dependent's parent_1_id and parent_2_id (natural, "
        "adoptive or step parents) decide the relationship where they "
        "settle it. A dependent is the head's child when either id names the "
        "head. A dependent is not when two different parents are named and "
        "neither is the head, when an id names another household member, or "
        "when the head's own parent ids name the dependent as the head's "
        "parent or grandparent. Otherwise, including when both ids are "
        "unknown (0), a dependent counts as the head's child unless marked "
        "as a parent or grandparent of the filer or as unrelated to the "
        "filer. Without parent ids the model cannot tell a child from a "
        "sibling, niece, nephew or grandchild."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/2#a_1_B",
        "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=15",
    )

    def formula(tax_unit, period, parameters):
        # The surviving spouse filing status should only apply to surviving spouse heads
        # who maintain a household for at least one dependent
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_surviving_spouse = person("is_surviving_spouse", period)
        surviving_spouse_head = tax_unit.any(is_head & is_surviving_spouse)
        # Without the 152(d)(1)(B) gross income test, the qualifying child,
        # disabled dependent and qualifying relative paths of
        # is_child_dependent together cover every tax unit dependent.
        is_dependent = person("is_tax_unit_dependent", period)

        # IRC 2(a)(1)(B)(i) limits the dependent to a son, stepson, daughter
        # or stepdaughter of the filer.
        unit = person.tax_unit.reference_entity.members_entity_id

        def is_unit_head(row):
            safe = np.maximum(row, 0)
            return (row >= 0) & is_head[safe] & (unit[safe] == unit)

        unit_parents = tax_unit_parent_indices(person, period)
        names_head = is_unit_head(unit_parents[0]) | is_unit_head(unit_parents[1])
        names_other_member = np.zeros(person.count, dtype=bool)
        for parent in co_resident_parent_indices(person, period):
            names_other_member |= (parent >= 0) & ~is_unit_head(parent)
        parent_1 = person("parent_1_id", period)
        parent_2 = person("parent_2_id", period)
        names_two_parents = (parent_1 != 0) & (parent_2 != 0) & (parent_1 != parent_2)
        # The head's own ids can name a dependent as the head's parent, and
        # that parent's ids as the head's grandparent.
        ancestor_of_head = np.zeros(person.count, dtype=bool)
        generation = is_head
        for _ in range(2):
            rows = np.concatenate([slot[generation] for slot in unit_parents])
            rows = rows[rows >= 0]
            ancestor_of_head[rows] = True
            generation = np.zeros(person.count, dtype=bool)
            generation[rows] = True
        not_child = (
            names_two_parents
            | names_other_member
            | ancestor_of_head
            | person("is_parent_of_filer_or_spouse", period)
            | person("is_grandparent_of_filer_or_spouse", period)
            | ~person("is_related_to_head_or_spouse", period)
        )
        is_child = names_head | ~not_child
        has_qualifying_child = tax_unit.any(is_dependent & is_child)
        married = tax_unit("tax_unit_married", period)
        return surviving_spouse_head & has_qualifying_child & ~married
