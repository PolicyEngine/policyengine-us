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
        "filer. A dependent is the head's child when their parent_1_id or "
        "parent_2_id (natural, adoptive or step parents) names the tax unit "
        "head. Because a parent id of 0 is unknown and a person can have more "
        "parents than the two ids hold, naming other parents does not rule a "
        "dependent out. The ids rule a dependent out only when they show "
        "another relationship to the head: the head's parent or grandparent, "
        "a sibling (a shared parent id), a grandchild (the dependent's parent "
        "names the head) or a niece or nephew (the dependent's parent shares "
        "a parent id with the head). Otherwise a dependent counts as the "
        "head's child unless marked as a parent or grandparent of the filer "
        "or as unrelated to the filer. Without such ids the model cannot tell "
        "a child from a sibling, niece, nephew or grandchild."
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
        # or stepdaughter of the filer. Each person's parents, as rows: both
        # id slots resolved among household members and among tax unit
        # members, -1 when unresolved.
        rows = np.arange(person.count)
        parent_rows = [
            *co_resident_parent_indices(person, period),
            *tax_unit_parent_indices(person, period),
        ]
        parent_ids = [person("parent_1_id", period), person("parent_2_id", period)]

        def parents_of(of):
            safe = np.maximum(of, 0)
            return [where(of >= 0, parent[safe], -1) for parent in parent_rows]

        def ids_of(of):
            safe = np.maximum(of, 0)
            return [where(of >= 0, ids[safe], 0) for ids in parent_ids]

        def shares_id(ids, other_ids):
            shared = np.zeros(person.count, dtype=bool)
            for a in ids:
                for b in other_ids:
                    shared |= (a != 0) & (a == b)
            return shared

        # Row of the head of each person's tax unit.
        unit = person.tax_unit.reference_entity.members_entity_id
        head_by_unit = np.full(tax_unit.count, -1)
        head_by_unit[unit[is_head]] = rows[is_head]
        head = head_by_unit[unit]
        head_parents = parents_of(head)
        head_ids = ids_of(head)

        names_head = np.zeros(person.count, dtype=bool)
        is_head_grandchild = np.zeros(person.count, dtype=bool)
        is_head_niece_or_nephew = np.zeros(person.count, dtype=bool)
        for parent in parent_rows:
            names_head |= (head >= 0) & (parent == head)
            for grandparent in parents_of(parent):
                is_head_grandchild |= (head >= 0) & (grandparent == head)
            is_head_niece_or_nephew |= (parent >= 0) & shares_id(
                ids_of(parent), head_ids
            )
        is_head_ancestor = np.zeros(person.count, dtype=bool)
        for parent in head_parents:
            is_head_ancestor |= parent == rows
            for grandparent in parents_of(parent):
                is_head_ancestor |= grandparent == rows
        is_head_sibling = shares_id(parent_ids, head_ids)

        not_child = (
            is_head_ancestor
            | is_head_sibling
            | is_head_grandchild
            | is_head_niece_or_nephew
            | person("is_parent_of_filer_or_spouse", period)
            | person("is_grandparent_of_filer_or_spouse", period)
            | ~person("is_related_to_head_or_spouse", period)
        )
        is_child = names_head | ~not_child
        has_qualifying_child = tax_unit.any(is_dependent & is_child)
        married = tax_unit("tax_unit_married", period)
        return surviving_spouse_head & has_qualifying_child & ~married
