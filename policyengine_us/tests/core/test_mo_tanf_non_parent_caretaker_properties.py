"""Invariants of Missouri TANF's non-parent caretaker relative (NPCR) rules.

13 CSR 40-2.300(5)(D) admits a needy non-parent caretaker relative or
guardian only when no parent is in the home, and lets one found eligible for
inclusion exclude themselves. DSS Manual 0210.005.35 sets the neediness
budget (NPCR and spouse against the full standard of need, after the $90 work
expense and child care but without the $30 plus one-third disregards) and
makes the NPCR needy without a budget when the spouse is absent or receives
SSI. DSS Manual 0210.005.15 forbids including an optional person when that
causes ineligibility or reduces the grant.

A seeded sample of households shares one simulation and is checked against
those rules, restated here independently of the variable formulas:

1. With no one marked as a non-parent caretaker, unit membership, countable
   resources and the teen-parent earnings exemption equal the pre-NPCR rule,
   plus the dependent adult parent, who is a member as a parent of the
   children (DSS Manual 0210.005.05; see
   test_mo_tanf_dependent_parent_properties.py).
2. Identification and neediness equal the restated rules: no NPCR when a
   parent is in the home (an unmarked caretaker, or a dependent adult with
   their own children in the household); otherwise the NPCR is needy when
   the spouse is absent or on SSI, or budget income is below the standard
   of need for the NPCR and spouse.
3. A needy NPCR who has not opted out gets the larger of the two grants; a
   non-needy or opted-out NPCR is excluded and the unit gets the children's
   grant. So opting out never raises the grant.
4. More income never turns a not-needy NPCR needy.
5. Marking a lone adult caretaker as a non-parent never lowers the grant
   when no parent is in the home. Two intended exceptions: a married NPCR
   can get less than an unmarked couple, because the spouse enters only the
   neediness budget, and a parent in the home excludes the NPCR.
6. The branch grants equal fresh simulations that fix the inclusion input,
   and every household gets the same answer alone as in the shared
   simulation.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

PERIOD = "2026-01"
YEAR = 2026
N = 480
SEED = 20260928
# 13 CSR 40-2.310(13) standard of need and (12) payment percentage.
STANDARD_OF_NEED = {1: 393, 2: 678, 3: 846, 4: 990, 5: 1_123}
PAYMENT_PERCENTAGE = 0.34526
WORK_EXPENSE = 90
RESOURCE_LIMIT = 1_000


def _households():
    rng = np.random.default_rng(SEED)
    households = []
    for _ in range(N):
        married = bool(rng.random() < 0.5)
        household = dict(
            married=married,
            head_flag=bool(rng.random() < 0.75),
            spouse_flag=bool(married and rng.random() < 0.8),
            head_ssi=bool(rng.random() < 0.15),
            spouse_ssi=bool(married and rng.random() < 0.2),
            children=int(rng.integers(1, 3)),
            child_ssi=bool(rng.random() < 0.15),
            head_unearned=int(rng.choice([0, 50, 100, 300, 400, 700, 1_200])),
            head_earned=int(rng.choice([0, 0, 100, 432, 900])),
            spouse_unearned=int(married and rng.choice([0, 0, 300, 700])),
            head_assets=int(rng.choice([0, 0, 800, 5_000])),
            spouse_assets=int(married and rng.choice([0, 5_000])),
            opts_out=bool(rng.random() < 0.2),
            # A dependent adult with a child of their own in the home, such
            # as a grandparent's adult daughter.
            adult_parent=bool(rng.random() < 0.1),
        )
        households.append(household)
    return households


HOUSEHOLDS = _households()


def _situation(households, **overrides):
    people, tax_units, spm_units, units = {}, {}, {}, {}
    for i, h in enumerate(households):
        h = {**h, **overrides}
        names = []

        def add(name, record):
            people[name] = record
            names.append(name)

        add(
            f"h{i}_head",
            {
                "age": {YEAR: 55},
                "is_tax_unit_dependent": {YEAR: False},
                "unemployment_compensation": {YEAR: 12 * h["head_unearned"]},
                "employment_income_before_lsr": {YEAR: 12 * h["head_earned"]},
                "bank_account_assets": {YEAR: h["head_assets"]},
                "receives_ssi": {YEAR: h["head_ssi"]},
                "mo_tanf_is_non_parent_caretaker": {YEAR: h["head_flag"]},
                "mo_tanf_non_parent_caretaker_opts_out": {YEAR: h["opts_out"]},
            },
        )
        if h["married"]:
            add(
                f"h{i}_spouse",
                {
                    "age": {YEAR: 53},
                    "is_tax_unit_dependent": {YEAR: False},
                    "unemployment_compensation": {YEAR: 12 * h["spouse_unearned"]},
                    "bank_account_assets": {YEAR: h["spouse_assets"]},
                    "receives_ssi": {YEAR: h["spouse_ssi"]},
                    "mo_tanf_is_non_parent_caretaker": {YEAR: h["spouse_flag"]},
                    "mo_tanf_non_parent_caretaker_opts_out": {YEAR: h["opts_out"]},
                },
            )
        if h["adult_parent"]:
            add(
                f"h{i}_adult_parent",
                {
                    "age": {YEAR: 22},
                    "is_tax_unit_dependent": {YEAR: True},
                    "own_children_in_household": {YEAR: 1},
                },
            )
        for c in range(h["children"]):
            add(
                f"h{i}_child{c}",
                {
                    "age": {YEAR: 6 + c},
                    "is_tax_unit_dependent": {YEAR: True},
                    "receives_ssi": {YEAR: h["child_ssi"] and c == 0},
                },
            )
        tax_units[f"t{i}"] = {"members": names}
        spm_units[f"s{i}"] = {"members": names}
        units[f"hh{i}"] = {"members": names, "state_code": {YEAR: "MO"}}
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "households": units,
    }


def _calc(sim, variable):
    return sim.calculate(variable, PERIOD)


@pytest.fixture(scope="module")
def sim():
    return Simulation(situation=_situation(HOUSEHOLDS))


@pytest.fixture(scope="module")
def unflagged_sim():
    return Simulation(
        situation=_situation(HOUSEHOLDS, head_flag=False, spouse_flag=False)
    )


def _person_index():
    """Per person: household index, role and child number, in situation order."""
    rows = []
    for i, h in enumerate(HOUSEHOLDS):
        rows.append((i, "head", None))
        if h["married"]:
            rows.append((i, "spouse", None))
        if h["adult_parent"]:
            rows.append((i, "adult_parent", None))
        rows.extend((i, "child", c) for c in range(h["children"]))
    return rows


PEOPLE = _person_index()


def _payment(size):
    return STANDARD_OF_NEED.get(size, 0) * PAYMENT_PERCENTAGE


def test_unflagged_households_include_dependent_parents(unflagged_sim):
    member = _calc(unflagged_sim, "mo_tanf_is_assistance_unit_member")
    assert not _calc(unflagged_sim, "mo_tanf_non_parent_caretaker").any()
    assert not _calc(unflagged_sim, "mo_tanf_non_parent_caretaker_included").any()
    # Every household has a dependent child, so each adult not on SSI is a
    # caretaker and each child not on SSI is an eligible child.
    expected = []
    for i, role, c in PEOPLE:
        h = HOUSEHOLDS[i]
        if role == "head":
            expected.append(not h["head_ssi"])
        elif role == "spouse":
            expected.append(not h["spouse_ssi"])
        elif role == "adult_parent":
            # A dependent aged 22 with a child of her own in the home is a
            # parent of the children, so she is a member (0210.005.05).
            expected.append(True)
        else:
            expected.append(not (h["child_ssi"] and c == 0))
    assert member.tolist() == expected
    # Resources: only SSI recipients' assets leave the aggregate.
    resources = _calc(unflagged_sim, "mo_tanf_countable_resources")
    for i, h in enumerate(HOUSEHOLDS):
        counted = (0 if h["head_ssi"] else h["head_assets"]) + (
            0 if h["spouse_ssi"] else h["spouse_assets"]
        )
        assert resources[i] == pytest.approx(counted)


def test_neediness_matches_the_restated_budget(sim):
    npcr = _calc(sim, "mo_tanf_non_parent_caretaker")
    needy = _calc(sim, "mo_tanf_non_parent_caretaker_needy")
    has_npcr = np.zeros(N, dtype=bool)
    npcr_is_head = np.zeros(N, dtype=bool)
    for k, (i, role, _) in enumerate(PEOPLE):
        if npcr[k]:
            assert not has_npcr[i], "at most one NPCR per unit"
            has_npcr[i] = True
            npcr_is_head[i] = role == "head"
    for i, h in enumerate(HOUSEHOLDS):
        # Restated identification: marked, head or spouse, not on SSI, no
        # unmarked (parent) caretaker, head first.
        parent_in_home = (
            (not h["head_flag"])
            or (h["married"] and not h["spouse_flag"])
            or h["adult_parent"]
        )
        head_ok = h["head_flag"] and not h["head_ssi"] and not parent_in_home
        spouse_ok = (
            h["married"]
            and h["spouse_flag"]
            and not h["spouse_ssi"]
            and not parent_in_home
        )
        assert has_npcr[i] == (head_ok or spouse_ok)
        if not has_npcr[i]:
            assert not needy[i]
            continue
        assert npcr_is_head[i] == head_ok
        if not h["married"]:
            expected = True
        else:
            other_ssi = h["spouse_ssi"] if head_ok else h["head_ssi"]
            if other_ssi:
                expected = True
            else:
                head_income = h["head_unearned"] + max(
                    h["head_earned"] - WORK_EXPENSE, 0
                )
                income = head_income + h["spouse_unearned"]
                expected = income < STANDARD_OF_NEED[2]
        assert needy[i] == expected, (i, h)


def test_inclusion_follows_the_optional_member_rule(sim):
    npcr = _calc(sim, "mo_tanf_non_parent_caretaker")
    needy = _calc(sim, "mo_tanf_non_parent_caretaker_needy")
    included = _calc(sim, "mo_tanf_non_parent_caretaker_included")
    grant = _calc(sim, "mo_tanf")
    if_included = _calc(sim, "mo_tanf_if_non_parent_caretaker_included")
    if_excluded = _calc(sim, "mo_tanf_if_non_parent_caretaker_excluded")
    member = _calc(sim, "mo_tanf_is_assistance_unit_member")
    size = _calc(sim, "mo_tanf_assistance_unit_size")
    for i, h in enumerate(HOUSEHOLDS):
        assert grant[i] >= 0
        assert grant[i] <= _payment(size[i]) + 1e-3
        if needy[i] and not h["opts_out"]:
            assert grant[i] == pytest.approx(max(if_included[i], if_excluded[i]))
        else:
            assert not included[i]
            assert grant[i] == pytest.approx(if_excluded[i])
        if included[i]:
            assert needy[i] and not h["opts_out"]
    # A non-included NPCR is never a unit member, and an included one is.
    for k, (i, _, _) in enumerate(PEOPLE):
        if npcr[k]:
            assert member[k] == included[i]


def test_opting_out_never_raises_the_grant(sim):
    opted = Simulation(situation=_situation(HOUSEHOLDS, opts_out=True))
    default = Simulation(situation=_situation(HOUSEHOLDS, opts_out=False))
    opted_grant = _calc(opted, "mo_tanf")
    default_grant = _calc(default, "mo_tanf")
    assert (opted_grant <= default_grant + 1e-3).all()
    assert not _calc(opted, "mo_tanf_non_parent_caretaker_included").any()


def test_more_income_never_makes_an_npcr_needy():
    richer = [{**h, "head_unearned": h["head_unearned"] + 250} for h in HOUSEHOLDS]
    base = Simulation(situation=_situation(HOUSEHOLDS))
    more = Simulation(situation=_situation(richer))
    base_needy = _calc(base, "mo_tanf_non_parent_caretaker_needy")
    more_needy = _calc(more, "mo_tanf_non_parent_caretaker_needy")
    assert not (more_needy & ~base_needy).any()


def test_marking_a_lone_caretaker_never_lowers_the_grant(sim, unflagged_sim):
    flagged = _calc(sim, "mo_tanf")
    unflagged = _calc(unflagged_sim, "mo_tanf")
    for i, h in enumerate(HOUSEHOLDS):
        lone = not h["married"] and not h["adult_parent"]
        if lone and h["head_flag"] and not h["opts_out"]:
            assert flagged[i] >= unflagged[i] - 1e-3, (i, h)


def test_married_npcr_can_receive_less_than_an_unmarked_couple():
    # Intended: 0210.005.35 budgets the spouse for neediness only, so the
    # included unit is the NPCR and children (size 3), not both adults.
    couple = dict(
        married=True,
        head_flag=True,
        spouse_flag=True,
        head_ssi=False,
        spouse_ssi=False,
        children=2,
        child_ssi=False,
        head_unearned=0,
        head_earned=0,
        spouse_unearned=0,
        head_assets=0,
        spouse_assets=0,
        opts_out=False,
        adult_parent=False,
    )
    flagged = Simulation(situation=_situation([couple]))
    unflagged = Simulation(
        situation=_situation([couple], head_flag=False, spouse_flag=False)
    )
    assert _calc(flagged, "mo_tanf")[0] == pytest.approx(_payment(3), abs=1e-3)
    assert _calc(unflagged, "mo_tanf")[0] == pytest.approx(_payment(4), abs=1e-3)


def test_branch_grants_match_fresh_simulations(sim):
    needy = _calc(sim, "mo_tanf_non_parent_caretaker_needy")
    for variable, fixed in (
        ("mo_tanf_if_non_parent_caretaker_included", needy),
        ("mo_tanf_if_non_parent_caretaker_excluded", np.zeros(N, dtype=bool)),
    ):
        fresh = Simulation(situation=_situation(HOUSEHOLDS))
        fresh.set_input("mo_tanf_non_parent_caretaker_included", PERIOD, fixed)
        assert _calc(sim, variable) == pytest.approx(_calc(fresh, "mo_tanf"), abs=1e-4)


@pytest.mark.parametrize("i", range(0, N, 16))
def test_each_household_alone_matches_the_shared_simulation(sim, i):
    alone = Simulation(situation=_situation([HOUSEHOLDS[i]]))
    for variable in (
        "mo_tanf_non_parent_caretaker_needy",
        "mo_tanf_non_parent_caretaker_included",
        "mo_tanf_assistance_unit_size",
        "mo_tanf",
    ):
        assert _calc(alone, variable)[0] == pytest.approx(_calc(sim, variable)[i])


@pytest.mark.parametrize("marked", [False, True])
def test_teen_parent_exemption_is_for_parents_only(marked):
    # 13 CSR 40-2.310(9)(A)6. exempts the earnings of a parent under 19 in
    # secondary school. Unmarked, the pre-NPCR rule holds; marked as a
    # non-parent caretaker, the exemption never applies. Ages 18 and 19 keep
    # the caretaker out of the dependent-child definition, whose student
    # exemption under (9)(A)1. would otherwise also apply.
    grid = [(age, school) for age in (18, 19) for school in (False, True)]
    people, tax_units, spm_units, units = {}, {}, {}, {}
    for i, (age, school) in enumerate(grid):
        people[f"t{i}_caretaker"] = {
            "age": {YEAR: age},
            "is_tax_unit_dependent": {YEAR: False},
            "is_in_secondary_school": {YEAR: school},
            "employment_income_before_lsr": {YEAR: 6_000},
            "mo_tanf_is_non_parent_caretaker": {YEAR: marked},
        }
        people[f"t{i}_child"] = {
            "age": {YEAR: 1},
            "is_tax_unit_dependent": {YEAR: True},
        }
        members = [f"t{i}_caretaker", f"t{i}_child"]
        tax_units[f"tu{i}"] = {"members": members}
        spm_units[f"su{i}"] = {"members": members}
        units[f"hh{i}"] = {"members": members, "state_code": {YEAR: "MO"}}
    teen_sim = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "spm_units": spm_units,
            "households": units,
        }
    )
    exempt = _calc(teen_sim, "is_mo_tanf_earned_income_exempt")
    for i, (age, school) in enumerate(grid):
        expected = (not marked) and age < 19 and school
        assert exempt[2 * i] == expected, (age, school, marked)
        assert not exempt[2 * i + 1]
