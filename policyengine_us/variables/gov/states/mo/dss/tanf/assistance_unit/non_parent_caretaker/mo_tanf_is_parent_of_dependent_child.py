from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    has_parent_ids,
)


class mo_tanf_is_parent_of_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Missouri TANF parent of a dependent child in the tax unit"
    documentation = (
        "Whether this person is the biological or adoptive parent of one of "
        "the tax unit's dependent children. Such a parent is a member of the "
        "assistance unit even when someone else claims them as a tax "
        "dependent, unless they receive SSI or are a dependent child "
        "themselves (then they are a member as a child). A parent in the "
        "home, other than a cash-eligible child, also excludes a non-parent "
        "caretaker. Reads January's dependent children in the person's tax "
        "unit. First uses each child's parent_1_id and parent_2_id, resolved "
        "to a co-resident person_id: a named parent qualifies regardless of "
        "ages or own_children_in_household. Only a child whose two parent "
        "ids are both unknown (0) permits the existing fallback: is_parent "
        "and an age gap of 12 to 50 years. Known ids naming another person "
        "or an absent parent do not permit age inference for that child. "
        "This follows d1049 and the principle to make inputs as leaf-nodey "
        "as possible; the age window imputes a relationship, not law. "
        "The fallback's own-child count can include adult children and "
        "children outside the tax unit, so supply parent ids when known, "
        "or set this input directly when the fallback does not match. "
        "Setting it for one "
        "person for a year sets it to false for everyone else not given a "
        "value for that year, so set it for every parent it applies to; other "
        "years still use the default. Heads and spouses not marked as "
        "non-parent caretakers retain their presumed-parent status only "
        "when a dependent child's parent ids are unknown, or this flag "
        "identifies them as a parent. This input cannot associate a "
        "parent filing a separate tax return with a child in another tax "
        "unit: even an explicit true leaves that parent excluded when their "
        "own tax unit has no dependent child. The assistance-unit formulas "
        "use tax-unit child grouping, so mandatory parent membership across "
        "tax units is not modeled."
    )
    definition_period = YEAR
    reference = (
        "https://my.mo.gov/cms_fsd?id=kb_article_view&sys_kb_id=98e1ef0c1b543650ba12657ae54bcbd1",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-05/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-10/",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # The flag is annual and reads January's dependent children, so a
        # change in who is a dependent child later in the year (for example
        # a child aging out through monthly_age inputs) does not update it.
        dependent_child = person("mo_tanf_dependent_child", period.first_month)
        # Use relationship leaf inputs first (Max's d1049). Resolve within
        # households using the shared helpers, so repeated ids in different
        # households cannot join unrelated families. Preserve the tax-unit
        # child grouping used by the assistance-unit formulas.
        tax_unit = person.tax_unit.reference_entity.members_entity_id
        linked_parent = np.zeros(person.count, dtype=bool)
        for parent in co_resident_parent_indices(person, period):
            relevant = dependent_child & (parent >= 0) & (tax_unit[parent] == tax_unit)
            linked_parent |= np.bincount(parent[relevant], minlength=person.count) > 0

        # Only fully unknown child links permit the unchanged 12–50 fallback.
        # Known but absent parents are still known and do not permit it.
        # Dependent children's ages span less than the 38-year window, so
        # the youngest/oldest shortcut is equivalent to checking each child.
        unknown_child = dependent_child & ~has_parent_ids(person, period)
        has_own_children = person("is_parent", period)
        age = person("age", period)
        youngest = person.tax_unit.min(where(unknown_child, age, np.inf))
        oldest = person.tax_unit.max(where(unknown_child, age, -np.inf))
        fallback = has_own_children & (age - youngest >= 12) & (age - oldest <= 50)
        return linked_parent | fallback
