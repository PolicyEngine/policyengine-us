from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_parents import (
    ssi_parental_deemors,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
    group_member_indices,
    has_parent_ids,
    household_has_parent_ids,
    household_member_indices,
    unlinked_parent,
)


def ssi_meets_eligibility_status(person, period):
    """Aged, blind or disabled, and a citizen or qualified noncitizen.

    Stands in for 'eligible for SSI benefits' when deciding who deems to whom.
    The income and resource tests are not read: they depend on deemed income.
    """
    immigration_status = person("immigration_status", period)
    is_citizen = immigration_status == immigration_status.possible_values.CITIZEN
    return person("is_ssi_aged_blind_disabled", period) & (
        is_citizen | person("is_ssi_qualified_noncitizen", period)
    )


def ssi_ineligible_parents(person, period, with_spouses=True):
    """Return each person's ineligible parents and their deemor pool.

    416.1160(d): an ineligible parent is 'a natural or adoptive parent, or
    the spouse ... of a natural or adoptive parent, who lives with you and is
    not eligible for SSI benefits'. ssi_parental_deemors resolves the parents
    and spouses from parent ids, or the tax-unit proxy without ids; this drops
    those who meet the SSI eligibility status (416.1165(g)(1)).

    Returns rows (the person's parents and parents' spouses, -1 padded), the
    mask of rows that are ineligible parents, and the pool of children who
    share the same parents. The tax-unit proxy keeps a person who is an
    unlinked parent in their own set, so that siblings keep one pool, but a
    person is never their own ineligible parent: deeming counts another
    person's income (416.1160(a)).
    """
    rows, pool = ssi_parental_deemors(person, period, with_spouses)
    eligible = ssi_meets_eligibility_status(person, period)
    own_index = np.arange(person.count)
    ineligible = (
        (rows >= 0) & (rows != own_index[:, None]) & ~eligible[np.maximum(rows, 0)]
    )
    return rows, ineligible, pool


def ssi_parental_deeming_child(person, period, ineligible, ssi_status=True):
    """Whether parental deeming applies to each person as an eligible child.

    POMS SI 01310.115 A.2: 'a natural or adopted child under age 18 who lives
    in a household with one or both parents, is not married, and is eligible
    for SSI'. 416.1856 also excludes the head of a household. Marriage uses
    the spouse test of SSI resource deeming. Eligibility is the SSI status
    condition: aged, blind or disabled and a citizen or qualified noncitizen.
    Without ssi_status, as for Medicaid, which applies its own immigration
    rules, being aged, blind or disabled suffices.
    """
    status = (
        ssi_meets_eligibility_status(person, period)
        if ssi_status
        else person("is_ssi_aged_blind_disabled", period)
    )
    return (
        person("is_child", period)
        & status
        & (_ssi_spouse_index(person, period) < 0)
        & ~person("is_household_head", period)
        & np.any(ineligible, axis=1)
    )


def _absent_spouses(person, period, rows):
    """The spouse, living elsewhere, of each of a person's parents (rows).

    A two-person marital unit whose members live in different households
    marks a spouse who lives elsewhere. When the simulation has a single
    marital unit, which may be the default group of a situation that omits
    marital units, no one is treated as such a spouse.
    """
    own_index = np.arange(person.count)
    couple = (person.marital_unit.nb_persons() == 2) & (person.marital_unit.count > 1)
    partner = np.full(person.count, -1, dtype=int)
    for member in group_member_indices(person.marital_unit):
        partner = np.where(
            couple & (member >= 0) & (member != own_index), member, partner
        )
    households = person.household.reference_entity.members_entity_id
    absent = np.where(
        (partner >= 0) & (households[np.maximum(partner, 0)] != households),
        partner,
        -1,
    )
    return np.where(rows >= 0, absent[np.maximum(rows, 0)], -1)


def ssi_parental_deeming_child_allocation_total(
    person, period, rows, every_minor=False, exclude=None
):
    """Sum the ineligible child allocations deducted for each person.

    416.1165(b) deducts 'an allocation for each ineligible child in the
    household'. 416.1160(d): an ineligible child is 'your natural child or
    adopted child, or ... the natural or adopted child of your parent or of
    your parent's spouse ... who lives in the same household with you'. So
    the children count when they are the person's own child or a child of one
    of the person's parents or parents' spouses (rows), whether or not that
    parent is eligible for SSI, as POMS SI 01310.115 A.3 and SI 01310.140 A
    describe. POMS SI 00501.010 B.2.d keeps the children of a stepparent who
    has left: 'If an SSI eligible child's stepparent has permanently left the
    household, we continue to provide the ineligible child allocation for
    each of the stepparent's children remaining in the eligible child's
    household', so the spouse of one of the parents who lives elsewhere also
    counts. A child with parent ids counts when an id names one of those
    people (an id that names no co-resident may name that absent spouse). A
    child without ids counts when they are in the tax unit of the person or
    of one of those people; in a household with links, only when the
    person, a parent or a parent's absent spouse is a parent some of whose
    children no id names (the parent-link contract in _parent_links.py). The parents themselves
    never count. every_minor (a bool or a per-person array) instead counts
    every co-resident child under 18 other than the person and their
    parents, as Missouri's MHDC budget does (DSS Manual 0805.020.15). People
    flagged in exclude never count.
    """
    every_minor = np.broadcast_to(every_minor, (person.count,))
    exclude = (
        np.zeros(person.count, dtype=bool)
        if exclude is None
        else np.broadcast_to(exclude, (person.count,))
    )
    allocation = person("ssi_ineligible_child_allocation", period)
    minor = person("is_child", period)
    first, second = co_resident_parent_indices(person, period)
    linked = has_parent_ids(person, period)
    unlinked = unlinked_parent(person, period)
    tax_unit = person.tax_unit.reference_entity.members_entity_id
    own_index = np.arange(person.count)
    # The person and their parents and parents' spouses.
    relatives = np.column_stack((own_index, rows))
    present = relatives >= 0
    safe_relatives = np.maximum(relatives, 0)
    relative_tax_units = np.where(present, tax_unit[safe_relatives], -1)
    # Spouses of the parents who live elsewhere, by person_id for children
    # whose ids name no co-resident, and by tax unit for the proxy.
    absent = _absent_spouses(person, period, rows)
    away = absent >= 0
    safe_absent = np.maximum(absent, 0)
    may_presume = (
        ~household_has_parent_ids(person, period)
        | np.any(present & unlinked[safe_relatives], axis=1)
        | np.any(away & unlinked[safe_absent], axis=1)
    )
    absent_ids = np.where(away, person("person_id", period)[safe_absent], 0)
    absent_tax_units = np.where(away, tax_unit[safe_absent], -1)
    parent_1 = person("parent_1_id", period)
    parent_2 = person("parent_2_id", period)
    total = np.zeros(person.count)
    for child in household_member_indices(person):
        safe = np.maximum(child, 0)
        # A second id that repeats the first is no second parent.
        unresolved_1 = np.where(first[safe] < 0, parent_1[safe], 0)
        unresolved_2 = np.where(
            (second[safe] < 0) & (parent_2[safe] != parent_1[safe]),
            parent_2[safe],
            0,
        )
        named = np.any(
            present
            & (
                (relatives == first[safe][:, None])
                | (relatives == second[safe][:, None])
            ),
            axis=1,
        ) | np.any(
            away
            & (
                ((unresolved_1 != 0)[:, None] & (absent_ids == unresolved_1[:, None]))
                | ((unresolved_2 != 0)[:, None] & (absent_ids == unresolved_2[:, None]))
            ),
            axis=1,
        )
        presumed = may_presume & (
            np.any(present & (relative_tax_units == tax_unit[safe][:, None]), axis=1)
            | np.any(away & (absent_tax_units == tax_unit[safe][:, None]), axis=1)
        )
        is_parent = np.any(present & (relatives == child[:, None]), axis=1)
        counts = (
            (child >= 0)
            & (child != own_index)
            & ~is_parent
            & ~exclude[safe]
            & where(
                every_minor,
                minor[safe],
                where(linked[safe], named, presumed),
            )
        )
        total += where(counts, allocation[safe], 0)
    return total


def ssi_parental_deeming_parent_allocation_total(parameters, period, parents):
    """The living allowance for a child's ineligible parents.

    416.1165(d)(3): the couple rate 'if both parents live with you', the
    individual rate 'if only one parent lives with you'. POMS SI 01320.500
    B.4 adds the couple rate plus the individual rate when both natural or
    adoptive parents and a stepparent live with the child (Example F.5); a
    couple rate for each pair and an individual rate for one left over
    extends that to any number.
    """
    p = parameters(period).gov.ssa.ssi.amount
    return (p.couple * (parents // 2) + p.individual * (parents % 2)) * MONTHS_IN_YEAR


def ssi_parental_deeming_children(pool, applies):
    """The number of children deeming applies to in each person's pool.

    416.1165(e)(2): 'If your parents have more than one eligible child under
    age 18 in the household, we divide the parental income to be deemed
    equally among those eligible children.'
    """
    count = np.bincount(pool[applies], minlength=int(np.max(pool, initial=-1)) + 1)
    return count[pool]


def ssi_parental_income(person, period, variable, rows, ineligible):
    """Total a variable over each person's ineligible parents."""
    values = person(variable, period)
    return np.sum(np.where(ineligible, values[np.maximum(rows, 0)], 0), axis=1)
