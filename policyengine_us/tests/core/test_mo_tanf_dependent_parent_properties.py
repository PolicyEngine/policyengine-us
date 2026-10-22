"""Invariants of Missouri TANF membership for parents claimed as tax dependents.

13 CSR 40-2.300(5)(C) and DSS Manual 0210.005.05 put the "biological or
adoptive parents of one or more of the eligible children" in the assistance
unit, whoever claims them for taxes. SSI recipients are excluded (13 CSR
40-2.310(1)(F)). A parent who is also a cash-eligible child is a member as a
child. For a minor parent (the grid's 16-year-old), DSS Manual 0210.005.30
lets that three-generation family file as one group. For an 18-year-old
parent in secondary school Max's d1049 approves interpretation (i); the
grid checks one combined unit with her baby and her own parent. A
non-parent caretaker relative is excluded while a parent is in the home
(0210.005.10).

Every combination in a grid of households shares one simulation and is
checked against those rules as restated here. Where an expectation still
reads a model output, the item says so:

1. Membership: children not on SSI; unmarked heads and spouses not on SSI;
   a tax-dependent adult when they are a dependent child, or when they are a
   parent of the children and not on SSI; a marked head or spouse only as the
   non-parent caretaker identified in item 2, when the model includes them.
   Inclusion (neediness and the grant comparison) is the model's own
   mo_tanf_non_parent_caretaker_included, not restated here.
2. Non-parent caretaker identification, person by person: with no parent in
   the home, the marked head, or the marked spouse when the head is on SSI;
   with a parent in the home, nobody. A dependent parent who is a member
   always excludes the non-parent caretaker.
3. Marking the dependent adult as a parent, against the same households with
   the adult marked not a parent, adds exactly that adult to the unit and
   removes, at most, an included non-parent caretaker. Both sides run the
   current code; the comparison does not execute the code before this rule.
4. Unit income is the sum of members' income, less the student exemption.
5. With no income anywhere, the grant is the payment standard for the unit
   size, and marking a parent never lowers it (against the model's grant
   with the adult marked not a parent), unless the parent receives SSI: then
   they stay out of the unit but still exclude the non-parent caretaker
   (intended).
6. The default input (own children in the household) gives the same answer
   as marking the parent directly, and each household gets the same answer
   alone as in the shared simulation.
7. With unknown parent IDs, the default marks a person with own children in
   the household only when some dependent child in the tax unit is 12 to
   50 years younger, checked pair by pair against the formula's
   youngest-and-oldest shortcut.
8. An explicit parent flag adds a person only when their own tax unit has a
   dependent child.
9. Known parent IDs identify the named parent independently of ages and
   own-child counts. Reusing IDs in separate households cannot link them.
10. Omitted and explicitly zero parent IDs preserve the frozen pre-d1049
    parent flags, NPCR identification, membership, unit sizes and zero-income
    grants, checked against independent expectations from b9e7fff.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

PERIOD = "2026-01"
YEAR = 2026
# 13 CSR 40-2.310(13) standard of need and (12) payment percentage.
STANDARD_OF_NEED = {1: 393, 2: 678, 3: 846, 4: 990, 5: 1_123, 6: 1_247}
PAYMENT_PERCENTAGE = 0.34526

# How the tax-dependent adult is described to the model.
#   parent: marked a parent of the children
#   non_parent: own_children_in_household = 1 but marked not a parent of the
#       children (for example the head's own mother)
#   ssi_parent: marked a parent, and receives SSI
#   own_children: only own_children_in_household = 1, leaving
#       mo_tanf_is_parent_of_dependent_child to its default. A situation that
#       sets an input for anyone sets it for everyone (unset people get the
#       default value, not the formula), so these households get a
#       simulation of their own.
ADULT_KINDS = ["parent", "non_parent", "ssi_parent"]
PARENT_KINDS = {"parent", "own_children", "ssi_parent"}


def _adult_configs():
    configs = [dict(adult=None)]
    for kind, age, school, earned, unearned in itertools.product(
        ADULT_KINDS, (18, 22), (False, True), (0, 300), (0, 150)
    ):
        configs.append(
            dict(
                adult=kind,
                adult_age=age,
                adult_school=school,
                adult_earned=earned,
                adult_unearned=unearned,
            )
        )
    return configs


def _households():
    households = []
    for marked, married, head_ssi, minor, child_ssi, adult in itertools.product(
        (False, True),
        (False, True),
        (False, True),
        (False, True),
        (False, True),
        _adult_configs(),
    ):
        households.append(
            dict(
                marked=marked,
                married=married,
                head_ssi=head_ssi,
                minor_parent=minor,
                child_ssi=child_ssi,
                **adult,
            )
        )
    return households


HOUSEHOLDS = _households()
N = len(HOUSEHOLDS)


def _roles(h):
    roles = ["head"]
    if h["married"]:
        roles.append("spouse")
    if h["adult"]:
        roles.append("adult")
    if h["minor_parent"]:
        roles += ["minor_parent", "baby"]
    roles.append("child")
    return roles


def _person(h, role, adult_kind=None):
    if role in ("head", "spouse"):
        record = {
            "age": {YEAR: 55 if role == "head" else 53},
            "is_tax_unit_dependent": {YEAR: False},
            "receives_ssi": {YEAR: role == "head" and h["head_ssi"]},
            "mo_tanf_is_non_parent_caretaker": {YEAR: h["marked"]},
        }
        if role == "head" and h["adult"] == "own_children":
            # The head's own children in the home are the dependent adult and
            # the 16-year-old mother, so the default marks the head a parent
            # too; the non-parent mark must still decide for a head.
            count = 1 + h["minor_parent"]
            record["own_children_in_household"] = {YEAR: count}
        return record
    if role == "adult":
        kind = adult_kind or h["adult"]
        record = {
            "age": {YEAR: h["adult_age"]},
            "is_tax_unit_dependent": {YEAR: True},
            "is_in_secondary_school": {YEAR: h["adult_school"]},
            "employment_income_before_lsr": {YEAR: 12 * h["adult_earned"]},
            "unemployment_compensation": {YEAR: 12 * h["adult_unearned"]},
            # SSI receipt stays with the household when adult_kind overrides
            # only whether the adult is marked a parent.
            "receives_ssi": {YEAR: h["adult"] == "ssi_parent"},
        }
        if kind != "parent" and kind != "ssi_parent":
            record["own_children_in_household"] = {YEAR: 1}
        if kind != "own_children":
            record["mo_tanf_is_parent_of_dependent_child"] = {
                YEAR: kind in PARENT_KINDS
            }
        return record
    if role == "minor_parent":
        return {
            "age": {YEAR: 16},
            "is_tax_unit_dependent": {YEAR: True},
            "own_children_in_household": {YEAR: 1},
        }
    if role == "baby":
        return {"age": {YEAR: 0}, "is_tax_unit_dependent": {YEAR: True}}
    return {
        "age": {YEAR: 6},
        "is_tax_unit_dependent": {YEAR: True},
        "receives_ssi": {YEAR: h["child_ssi"]},
    }


def _situation(households, adult_kind=None):
    people, tax_units, spm_units, units = {}, {}, {}, {}
    for i, h in enumerate(households):
        names = []
        for role in _roles(h):
            name = f"h{i}_{role}"
            people[name] = _person(h, role, adult_kind)
            names.append(name)
        tax_units[f"t{i}"] = {"members": names}
        spm_units[f"s{i}"] = {"members": names}
        units[f"hh{i}"] = {"members": names, "state_code": {YEAR: "MO"}}
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "households": units,
    }


PEOPLE = [(i, role) for i, h in enumerate(HOUSEHOLDS) for role in _roles(h)]


def _calc(sim, variable):
    return sim.calculate(variable, PERIOD)


def _payment(size):
    return STANDARD_OF_NEED.get(int(size), 0) * PAYMENT_PERCENTAGE


def _adult_is_dependent_child(h):
    # 13 CSR 40-2.325(1)(A): under 18, or 18 and in secondary school.
    return h["adult"] is not None and h["adult_age"] == 18 and h["adult_school"]


def _adult_is_parent(h, kind=None):
    kind = kind or h["adult"]
    return kind in PARENT_KINDS


def _parent_in_home(h, kind=None):
    """A parent of the children lives in the home (DSS Manual 0210.005.10)."""
    unmarked_caretaker = not h["marked"]
    adult_ssi = h["adult"] == "ssi_parent"
    # A parent who is a cash-eligible child does not count (0210.005.05); the
    # 16-year-old mother is always one.
    cash_eligible_child = _adult_is_dependent_child(h) and not adult_ssi
    adult_parent = (
        h["adult"] is not None and _adult_is_parent(h, kind) and not cash_eligible_child
    )
    return unmarked_caretaker or adult_parent


def _expected_non_parent_caretaker(h, role):
    """The non-parent caretaker considered for the unit, restated.

    13 CSR 40-2.300(5)(D) admits one only "if there are no natural or
    adoptive parents in the home"; DSS Manual 0210.005.35 bars one on SSI.
    One per couple: the head, or the spouse when the head is on SSI. Only
    the head and spouse are marked, and the spouse is never on SSI here.
    """
    eligible = h["marked"] and not _parent_in_home(h)
    if role == "head":
        return eligible and not h["head_ssi"]
    if role == "spouse":
        return eligible and h["head_ssi"]
    return False


def _expected_member(h, role, kind=None):
    """Restated membership, or None where the non-parent caretaker rules decide."""
    kind = kind or h["adult"]
    if role == "head":
        if not h["marked"]:
            return not h["head_ssi"]
        return None
    if role == "spouse":
        return None if h["marked"] else True
    if role == "adult":
        ssi = h["adult"] == "ssi_parent"
        if _adult_is_dependent_child(h):
            return not ssi
        return _adult_is_parent(h, kind) and not ssi
    if role in ("minor_parent", "baby"):
        return True
    return not h["child_ssi"]


@pytest.fixture(scope="module")
def sim():
    return Simulation(situation=_situation(HOUSEHOLDS))


@pytest.fixture(scope="module")
def non_parent_sim():
    # The same households with the dependent adult marked as not a parent of
    # the children: the rule before parents claimed as dependents were members.
    return Simulation(situation=_situation(HOUSEHOLDS, adult_kind="non_parent"))


def test_membership_matches_the_restated_rule(sim):
    member = _calc(sim, "mo_tanf_is_assistance_unit_member")
    # Inclusion of an identified caretaker is the model's own decision.
    included = _calc(sim, "mo_tanf_non_parent_caretaker_included")
    for k, (i, role) in enumerate(PEOPLE):
        h = HOUSEHOLDS[i]
        expected = _expected_member(h, role)
        if expected is None:
            # A marked head or spouse is a member only as the identified
            # non-parent caretaker, and only when included.
            npcr = _expected_non_parent_caretaker(h, role)
            assert member[k] == (npcr and included[i]), (h, role)
        else:
            assert member[k] == expected, (h, role)


def test_non_parent_caretaker_identification_matches_independent_rule(sim):
    npcr = _calc(sim, "mo_tanf_non_parent_caretaker")
    expected = np.array(
        [_expected_non_parent_caretaker(HOUSEHOLDS[i], role) for i, role in PEOPLE]
    )
    mismatches = [
        (HOUSEHOLDS[i], role, bool(npcr[k]))
        for k, (i, role) in enumerate(PEOPLE)
        if npcr[k] != expected[k]
    ]
    assert not mismatches, mismatches[:5]
    has_npcr = np.zeros(N, dtype=bool)
    for k, (i, role) in enumerate(PEOPLE):
        has_npcr[i] |= npcr[k]
    expected_has_npcr = np.array(
        [
            h["marked"]
            and not _parent_in_home(h)
            and (not h["head_ssi"] or h["married"])
            for h in HOUSEHOLDS
        ]
    )
    assert has_npcr.tolist() == expected_has_npcr.tolist()
    # The grid has households where a caretaker must be found and where none
    # may be, so neither "never" nor "always" passes.
    assert expected_has_npcr.any() and not expected_has_npcr.all()


def test_a_dependent_parent_member_excludes_the_non_parent_caretaker(sim):
    member = _calc(sim, "mo_tanf_is_assistance_unit_member")
    npcr = _calc(sim, "mo_tanf_non_parent_caretaker")
    has_npcr = np.zeros(N, dtype=bool)
    parent_member = np.zeros(N, dtype=bool)
    for k, (i, role) in enumerate(PEOPLE):
        has_npcr[i] |= npcr[k]
        if role == "adult" and not _adult_is_dependent_child(HOUSEHOLDS[i]):
            parent_member[i] |= member[k]
    assert parent_member.any()
    assert not (parent_member & has_npcr).any()
    # A parent in the home rules out a caretaker; the converse, that one is
    # found when no parent is home, is in the identification test above.
    for i, h in enumerate(HOUSEHOLDS):
        if _parent_in_home(h):
            assert not has_npcr[i], h


def test_marking_a_parent_adds_only_that_parent(sim, non_parent_sim):
    on = _calc(sim, "mo_tanf_is_assistance_unit_member")
    off = _calc(non_parent_sim, "mo_tanf_is_assistance_unit_member")
    off_npcr = _calc(non_parent_sim, "mo_tanf_non_parent_caretaker")
    for k, (i, role) in enumerate(PEOPLE):
        if on[k] and not off[k]:
            assert role == "adult", (HOUSEHOLDS[i], role)
        if off[k] and not on[k]:
            # Only an included non-parent caretaker can leave, displaced by
            # the parent now seen in the home.
            assert off_npcr[k], (HOUSEHOLDS[i], role)
    # With the adult marked not a parent, a dependent adult who is not a
    # dependent child is never a member. This runs the current code with
    # that input, not the code before parents claimed as dependents counted.
    for k, (i, role) in enumerate(PEOPLE):
        if role == "adult" and not _adult_is_dependent_child(HOUSEHOLDS[i]):
            assert not off[k]


def test_unit_income_is_members_income(sim):
    member = _calc(sim, "mo_tanf_is_assistance_unit_member")
    earned = _calc(sim, "mo_tanf_gross_earned_income")
    unearned = _calc(sim, "mo_tanf_gross_unearned_income")
    expected_earned = np.zeros(N)
    expected_unearned = np.zeros(N)
    for k, (i, role) in enumerate(PEOPLE):
        h = HOUSEHOLDS[i]
        if role != "adult" or not member[k]:
            continue
        expected_unearned[i] += h["adult_unearned"]
        # 13 CSR 40-2.310(9)(A)1: a student dependent child's earnings are
        # exempt.
        if not _adult_is_dependent_child(h):
            expected_earned[i] += h["adult_earned"]
    assert earned == pytest.approx(expected_earned)
    assert unearned == pytest.approx(expected_unearned)


def test_zero_income_grant_is_the_payment_standard(sim, non_parent_sim):
    size = _calc(sim, "mo_tanf_assistance_unit_size")
    grant = _calc(sim, "mo_tanf")
    off_grant = _calc(non_parent_sim, "mo_tanf")
    checked = 0
    for i, h in enumerate(HOUSEHOLDS):
        assert 0 <= grant[i] <= _payment(size[i]) + 1e-3
        no_income = h["adult"] is None or (
            h["adult_earned"] == 0 and h["adult_unearned"] == 0
        )
        if not no_income:
            continue
        checked += 1
        assert grant[i] == pytest.approx(_payment(size[i]), abs=1e-3), h
        # A parent with no income adds needs and no income, so marking them
        # never lowers the grant. Intended exception: a parent on SSI is not a
        # member but still excludes the non-parent caretaker (0210.005.10).
        if h["adult"] != "ssi_parent":
            assert grant[i] >= off_grant[i] - 1e-3, h
    assert checked > N / 4


def test_default_input_matches_marking_the_parent():
    marked = [h for h in HOUSEHOLDS if h["adult"] == "parent"]
    own_children = [{**h, "adult": "own_children"} for h in marked]
    default_sim = Simulation(situation=_situation(own_children))
    marked_sim = Simulation(situation=_situation(marked))
    flag = default_sim.calculate("mo_tanf_is_parent_of_dependent_child", YEAR)
    roles = [role for h in own_children for role in _roles(h)]
    # The default is own_children_in_household > 0 and being 12 to 50 years
    # older than some dependent child in the tax unit. Here the head (55),
    # the dependent adult (18 or 22) and the 16-year-old mother all have
    # their own children in the home and pass the age window; nobody else
    # has own children.
    assert flag.tolist() == [
        role in ("head", "adult", "minor_parent") for role in roles
    ]
    member = _calc(default_sim, "mo_tanf_is_assistance_unit_member")
    k = 0
    for h in own_children:
        for role in _roles(h):
            expected = _expected_member(h, role)
            if expected is not None:
                assert member[k] == expected, (h, role)
            k += 1
    for variable in (
        "mo_tanf_is_assistance_unit_member",
        "mo_tanf_non_parent_caretaker",
        "mo_tanf_assistance_unit_size",
        "mo_tanf",
    ):
        assert _calc(default_sim, variable) == pytest.approx(
            _calc(marked_sim, variable)
        ), variable


@pytest.mark.parametrize("i", range(0, N, 97))
def test_each_household_alone_matches_the_shared_simulation(sim, i):
    alone = Simulation(situation=_situation([HOUSEHOLDS[i]]))
    for variable in ("mo_tanf_assistance_unit_size", "mo_tanf"):
        assert _calc(alone, variable)[0] == pytest.approx(_calc(sim, variable)[i])


def test_parent_flag_needs_a_dependent_child_in_the_persons_tax_unit():
    # Each household: a mother (30) heading a tax unit with her 5-year-old,
    # and an adult explicitly marked a parent who either files alone (no
    # dependent child in their tax unit) or is claimed in the mother's unit.
    cases = list(itertools.product((18, 25, 40, 60), (False, True)))
    people, tax_units, spm_units, units = {}, {}, {}, {}
    for i, (age, files_alone) in enumerate(cases):
        mother, child, adult = (f"g{i}_{r}" for r in ("mother", "child", "adult"))
        people[mother] = {"age": {YEAR: 30}, "is_tax_unit_dependent": {YEAR: False}}
        people[child] = {"age": {YEAR: 5}, "is_tax_unit_dependent": {YEAR: True}}
        people[adult] = {
            "age": {YEAR: age},
            "is_tax_unit_dependent": {YEAR: not files_alone},
            "mo_tanf_is_parent_of_dependent_child": {YEAR: True},
        }
        if files_alone:
            tax_units[f"g{i}_family"] = {"members": [mother, child]}
            tax_units[f"g{i}_adult"] = {"members": [adult]}
        else:
            tax_units[f"g{i}_family"] = {"members": [mother, child, adult]}
        spm_units[f"g{i}_spm"] = {"members": [mother, child, adult]}
        units[f"g{i}_hh"] = {
            "members": [mother, child, adult],
            "state_code": {YEAR: "MO"},
        }
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "spm_units": spm_units,
            "households": units,
        }
    )
    member = _calc(simulation, "mo_tanf_is_assistance_unit_member")
    size = _calc(simulation, "mo_tanf_assistance_unit_size")
    grant = _calc(simulation, "mo_tanf")
    for i, (age, files_alone) in enumerate(cases):
        expected = [True, True, not files_alone]
        assert member[3 * i : 3 * i + 3].tolist() == expected, (age, files_alone)
        assert size[i] == sum(expected), (age, files_alone)
        assert grant[i] == pytest.approx(_payment(sum(expected)), abs=1e-3)


def test_default_parent_input_matches_the_pairwise_age_rule():
    # The default is own_children_in_household > 0 and being 12 to 50 years
    # older than some dependent child in the tax unit. The formula checks only
    # the youngest and oldest child; restate it pair by pair here.
    adult_ages = [14, 17, 19, 22, 30, 40, 45, 50, 55, 58, 60, 62, 64, 68, 70, 80]
    # Each entry: ages of the other children, and whether an 18-year-old
    # secondary-school student (a dependent child) is also in the unit.
    child_sets = [
        ([0], False),
        ([8], False),
        ([10], False),
        ([17], False),
        ([0, 17], False),
        ([5, 12], False),
        ([2], True),
        ([], True),
    ]
    cases = [
        (age, children, student, own)
        for age, (children, student), own in itertools.product(
            adult_ages, child_sets, (0, 1)
        )
    ]
    people, tax_units, spm_units, units = {}, {}, {}, {}
    for i, (age, children, student, own) in enumerate(cases):
        names = [f"c{i}_head", f"c{i}_person"]
        people[names[0]] = {"age": {YEAR: 45}, "is_tax_unit_dependent": {YEAR: False}}
        people[names[1]] = {
            "age": {YEAR: age},
            "is_tax_unit_dependent": {YEAR: True},
            "own_children_in_household": {YEAR: own},
        }
        for j, child_age in enumerate(children):
            names.append(f"c{i}_child{j}")
            people[names[-1]] = {
                "age": {YEAR: child_age},
                "is_tax_unit_dependent": {YEAR: True},
            }
        if student:
            names.append(f"c{i}_student")
            people[names[-1]] = {
                "age": {YEAR: 18},
                "is_tax_unit_dependent": {YEAR: True},
                "is_in_secondary_school": {YEAR: True},
            }
        tax_units[f"t{i}"] = {"members": names}
        spm_units[f"s{i}"] = {"members": names}
        units[f"hh{i}"] = {"members": names, "state_code": {YEAR: "MO"}}
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "spm_units": spm_units,
            "households": units,
        }
    )
    flag = simulation.calculate("mo_tanf_is_parent_of_dependent_child", YEAR)
    position = 0
    for age, children, student, own in cases:
        person_flag = flag[position + 1]
        position += 2 + len(children) + student
        child_ages = list(children) + ([18] if student else [])
        # A person under 18 is a dependent child too, but their own age
        # difference of zero never falls in the window.
        plausible = any(12 <= age - c <= 50 for c in child_ages)
        assert person_flag == (own > 0 and plausible), (age, children, student, own)


def test_known_parent_ids_override_ages_and_stay_within_households():
    # Pin dependency status to isolate parent identification from the age
    # rules deciding who is a dependent child. The expected relationship
    # stays the same across adult and child ages and both own-child counts.
    cases = list(
        itertools.product(
            (19, 20, 35, 60, 90),
            (0, 5, 17),
            (0, 1),
            ("first", "second", "both"),
            ("adult", "head", "absent"),
        )
    )
    people, tax_units, spm_units, households = {}, {}, {}, {}
    expected = []
    for i, (adult_age, child_age, own_children, slot, parent) in enumerate(cases):
        head, adult, child = (
            f"linked{i}_{role}" for role in ("head", "adult", "child")
        )
        named_id = {"head": 11, "adult": 22, "absent": 99}[parent]
        # The ID contract allows these IDs to repeat in separate households
        # when every tax unit stays within its household. This deliberately
        # catches a global match that connects unrelated households.
        people[head] = {
            "person_id": {YEAR: 11},
            "age": {YEAR: 45},
            "is_tax_unit_dependent": {YEAR: False},
            "own_children_in_household": {YEAR: 1},
            "mo_tanf_dependent_child": {PERIOD: False},
        }
        people[adult] = {
            "person_id": {YEAR: 22},
            "age": {YEAR: adult_age},
            "is_tax_unit_dependent": {YEAR: True},
            "own_children_in_household": {YEAR: own_children},
            "mo_tanf_dependent_child": {PERIOD: False},
        }
        people[child] = {
            "person_id": {YEAR: 33},
            "age": {YEAR: child_age},
            "is_tax_unit_dependent": {YEAR: True},
            "mo_tanf_dependent_child": {PERIOD: True},
            "parent_1_id": {YEAR: named_id if slot in ("first", "both") else 0},
            "parent_2_id": {YEAR: named_id if slot in ("second", "both") else 0},
        }
        members = [head, adult, child]
        tax_units[f"linked{i}_tax"] = {"members": members}
        spm_units[f"linked{i}_spm"] = {"members": members}
        households[f"linked{i}_household"] = {
            "members": members,
            "state_code": {YEAR: "MO"},
        }
        expected.append([parent == "head", parent == "adult", False])
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "spm_units": spm_units,
            "households": households,
        }
    )
    flag = simulation.calculate("mo_tanf_is_parent_of_dependent_child", YEAR)
    for case, actual, wanted in zip(cases, flag.reshape(-1, 3), expected):
        assert actual.tolist() == wanted, case


@pytest.mark.parametrize("explicit_zero_ids", (False, True))
def test_unknown_parent_ids_reproduce_the_frozen_pre_d1049_rule(explicit_zero_ids):
    """Unknown ids preserve pre-d1049 flags, caretakers, members, sizes and grants.

    Independently restate the three changed formulas at immutable commit
    b9e7fff948caf4f33313c942c09caa7c7ccc3dea, rather than reading any current
    model output to construct expectations. Cover 224 households (784 people)
    for each of omitted parent ids and explicitly zero parent ids. The grid
    includes both age-window boundaries, own-child counts, caretaker markings,
    couples, SSI exclusions and an 18-year-old secondary-school student.
    """
    cases = list(
        itertools.product(
            (
                (11, False),
                (12, False),
                (18, False),
                (18, True),
                (19, False),
                (50, False),
                (51, False),
            ),
            (0, 1),
            (False, True),
            (False, True),
            ("none", "head", "adult", "child"),
        )
    )
    people, tax_units, spm_units, households = {}, {}, {}, {}
    expected = {
        "mo_tanf_is_parent_of_dependent_child": [],
        "mo_tanf_non_parent_caretaker": [],
        "mo_tanf_is_assistance_unit_member": [],
        "mo_tanf_assistance_unit_size": [],
        "mo_tanf": [],
    }
    for i, ((adult_age, student), own, marked, married, ssi_role) in enumerate(cases):
        roles = np.array(
            ["head"] + (["spouse"] if married else []) + ["adult", "child"]
        )
        ages = np.array(
            [
                {"head": 55, "spouse": 53, "adult": adult_age, "child": 0}[role]
                for role in roles
            ]
        )
        own_children = np.where(roles == "adult", own, 0)
        dependent_child = (roles == "child") | (
            (roles == "adult") & ((adult_age < 18) | ((adult_age == 18) & student))
        )
        receives_ssi = roles == ssi_role
        caretaker = np.isin(roles, ("head", "spouse"))
        non_parent = caretaker & marked

        # Frozen b9e7fff parent formula, expressed pairwise instead of through
        # the youngest/oldest shortcut. Unknown ids must retain this fallback.
        parent = np.array(
            [
                count > 0
                and any(
                    12 <= age - child_age <= 50 for child_age in ages[dependent_child]
                )
                for age, count in zip(ages, own_children)
            ]
        )
        cash_eligible_child = dependent_child & ~receives_ssi
        parent_in_home = np.any(
            (caretaker | (parent & ~cash_eligible_child)) & ~non_parent
        )
        candidate = caretaker & non_parent & ~parent_in_home & ~receives_ssi
        # Frozen b9e7fff NPCR formula: head first, otherwise the spouse.
        npcr = candidate & ((roles == "head") | ~candidate[0])
        # With zero non-SSI income and resources, every identified NPCR is
        # needy and adding their needs raises the grant, so they are included.
        member = (
            cash_eligible_child
            | (caretaker & ~non_parent & ~receives_ssi)
            | (parent & ~non_parent & ~dependent_child & ~receives_ssi)
            | npcr
        )
        expected["mo_tanf_is_parent_of_dependent_child"].extend(parent)
        expected["mo_tanf_non_parent_caretaker"].extend(npcr)
        expected["mo_tanf_is_assistance_unit_member"].extend(member)
        expected["mo_tanf_assistance_unit_size"].append(int(member.sum()))
        expected["mo_tanf"].append(_payment(member.sum()))

        names = []
        for role, age, count, ssi in zip(roles, ages, own_children, receives_ssi):
            name = f"unknown{i}_{role}"
            names.append(name)
            people[name] = {
                "age": {YEAR: int(age)},
                "is_tax_unit_head": {YEAR: bool(role == "head")},
                "is_tax_unit_spouse": {YEAR: bool(role == "spouse")},
                "is_tax_unit_dependent": {YEAR: role in ("adult", "child")},
                "own_children_in_household": {YEAR: int(count)},
                "is_in_secondary_school": {YEAR: bool(role == "adult" and student)},
                "mo_tanf_is_non_parent_caretaker": {
                    YEAR: role in ("head", "spouse") and marked
                },
                # Freeze both SSI signals; computing SSI from otherwise empty
                # income inputs would introduce unrelated benefit eligibility.
                "receives_ssi": {YEAR: bool(ssi)},
                "ssi": {PERIOD: 100 if ssi else 0},
                "employment_income_before_lsr": {YEAR: 0},
                "unemployment_compensation": {YEAR: 0},
            }
            if explicit_zero_ids:
                people[name]["parent_1_id"] = {YEAR: 0}
                people[name]["parent_2_id"] = {YEAR: 0}
        tax_units[f"unknown{i}_tax"] = {"members": names}
        spm_units[f"unknown{i}_spm"] = {"members": names}
        households[f"unknown{i}_household"] = {
            "members": names,
            "state_code": {YEAR: "MO"},
        }

    assert len(cases) == 224 and len(people) == 784
    # Both sides of each boolean rule occur, so constant outputs cannot pass.
    for variable in (
        "mo_tanf_is_parent_of_dependent_child",
        "mo_tanf_non_parent_caretaker",
        "mo_tanf_is_assistance_unit_member",
    ):
        assert any(expected[variable]) and not all(expected[variable]), variable
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "spm_units": spm_units,
            "households": households,
        }
    )
    for variable, values in expected.items():
        period = YEAR if variable == "mo_tanf_is_parent_of_dependent_child" else PERIOD
        actual = simulation.calculate(variable, period)
        if variable == "mo_tanf":
            np.testing.assert_allclose(
                actual, values, rtol=0, atol=1e-3, err_msg=variable
            )
        else:
            np.testing.assert_array_equal(actual, values, err_msg=variable)
