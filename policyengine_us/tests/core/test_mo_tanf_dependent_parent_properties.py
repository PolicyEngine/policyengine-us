"""Invariants of Missouri TANF membership for parents claimed as tax dependents.

13 CSR 40-2.300(5)(C) and DSS Manual 0210.005.05 put the "biological or
adoptive parents of one or more of the eligible children" in the assistance
unit, whoever claims them for taxes. SSI recipients are excluded (13 CSR
40-2.310(1)(F)). A parent who is also a cash-eligible child is a member as a
child, and DSS Manual 0210.005.30 lets that three-generation family file as
one group. A non-parent caretaker relative is excluded while a parent is in
the home (0210.005.10).

Every combination in a grid of households shares one simulation and is
checked against those rules, restated here independently of the formulas:

1. Membership: children not on SSI; unmarked heads and spouses not on SSI;
   a tax-dependent adult when they are a dependent child, or when they are a
   parent of the children and not on SSI; a marked head or spouse only as an
   included non-parent caretaker, which needs no parent in the home.
2. A dependent parent who is a member always excludes the non-parent
   caretaker.
3. Marking the dependent adult as a parent adds exactly that adult to the
   unit and removes, at most, an included non-parent caretaker.
4. Unit income is the sum of members' income, less the student exemption.
5. With no income anywhere, the grant is the payment standard for the unit
   size, and marking a parent never lowers it, unless the parent receives
   SSI: then they stay out of the unit but still exclude the non-parent
   caretaker (intended).
6. The default input (own children in the household) gives the same answer
   as marking the parent directly, and each household gets the same answer
   alone as in the shared simulation.
7. The default marks a person with own children in the household only when
   some dependent child in the tax unit is 12 to 50 years younger, checked
   pair by pair against the formula's youngest-and-oldest shortcut.
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
    npcr = _calc(sim, "mo_tanf_non_parent_caretaker")
    included = _calc(sim, "mo_tanf_non_parent_caretaker_included")
    for k, (i, role) in enumerate(PEOPLE):
        h = HOUSEHOLDS[i]
        expected = _expected_member(h, role)
        if expected is None:
            # A marked head or spouse is a member only as an included
            # non-parent caretaker, which requires no parent in the home.
            assert member[k] == (npcr[k] and included[i]), (h, role)
            if member[k]:
                assert not _parent_in_home(h), (h, role)
        else:
            assert member[k] == expected, (h, role)


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
    # The non-parent caretaker rules see a parent in the home exactly when
    # the restated rule does.
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
    # Before this rule, a dependent adult who is not a dependent child was
    # never a member.
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
    # The default is own_children_in_household > 0: the head, the dependent
    # adult and the 16-year-old mother, nobody else.
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
