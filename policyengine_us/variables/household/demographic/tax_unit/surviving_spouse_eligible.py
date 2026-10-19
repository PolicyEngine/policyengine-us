from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    household_has_parent_ids,
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
        "filer. A dependent is the filer's child when their parent_1_id or "
        "parent_2_id names the tax unit head; these ids cover natural, "
        "adoptive and step parents. In a household with no parent ids, every "
        "dependent counts as a child unless marked as a parent or grandparent "
        "of the filer or as unrelated to the filer."
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
        names_head = np.zeros(person.count, dtype=bool)
        for parent in tax_unit_parent_indices(person, period):
            names_head |= (parent >= 0) & is_head[np.maximum(parent, 0)]
        marked_not_child = (
            person("is_parent_of_filer_or_spouse", period)
            | person("is_grandparent_of_filer_or_spouse", period)
            | ~person("is_related_to_head_or_spouse", period)
        )
        is_child = where(
            household_has_parent_ids(person, period),
            names_head,
            ~marked_not_child,
        )
        has_qualifying_child = tax_unit.any(is_dependent & is_child)
        married = tax_unit("tax_unit_married", period)
        return surviving_spouse_head & has_qualifying_child & ~married
