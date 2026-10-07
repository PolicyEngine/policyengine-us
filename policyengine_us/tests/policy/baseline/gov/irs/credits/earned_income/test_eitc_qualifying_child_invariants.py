"""Invariants of the EITC qualifying-child test and the DC EITC branches.

Hypothesis draws earnings, investment income and ages. Each draw becomes one
vectorized simulation holding every combination of dependent, identification
status and state, so each property is checked on every combination for the
drawn incomes.

EITC qualifying child (IRC 32(c)(3)(A), applying IRC 152(c)):

1. A dependent flagged as a parent or grandparent of the filer is never an
   EITC qualifying child. The IRC 152(c)(3)(B) disability waiver reaches only
   the age test, not the IRC 152(c)(2) relationship test.
2. Relationship dominates disability: for a parent or grandparent dependent,
   the disability flag changes no EITC-style credit (federal, CA, CO, DC, IL,
   MN, WA).
3. Disability monotonicity: making an adult child dependent disabled never
   moves a DC unit from the with-child schedule to the childless one.

DC EITC (D.C. Code 47-1806.04(f)):

4. Both branches are non-negative, at most one is positive, and dc_eitc
   equals the branch selected by dc_eitc_has_qualifying_child, which is also
   max(with, without).
5. The with-child branch is zero without a qualifying child, and the
   childless branch is zero with one.
6. Before 2023, the with-child branch is the match times the federal credit
   allowed (a differential check against the federal eitc variable).
7. Before 2023 an ITIN filer receives no DC EITC, and giving a qualifying
   child an ITIN instead of a Social Security number never raises dc_eitc.
8. From 2023, giving a qualifying child an ITIN instead of a Social Security
   number leaves dc_eitc unchanged (D.C. Code 47-1806.04(f)(1)(D)(ii)).
9. A qualifying child with an ITIN routes its unit like one with a Social
   Security number in every year; before 2023 it is still a qualifying child,
   only left out of the IRC 32(b) computation. A qualifying child with
   neither number counts for nothing: the unit gets the same routing and the
   same dc_eitc as the same filer with no dependent. The D-40 instructions
   say so from 2023 (Line 27a), and the model keeps that treatment for
   earlier years (qualifying_child_tin_required).
10. From 2023, removing a qualifying child's TIN never raises dc_eitc. Before
    2023 it can, as intended: DC's childless schedule can pay more than the
    with-child match on the federal credit allowed. In TY2022 at $6,000 of
    earnings, an ITIN child gives 70% x 459 = 321.30 and a child with no
    number gives the childless 459.

With qualifying_child_tin_required switched off, the reading of (f)(4) and
IRC 32(c)(3)(D) alone:

11. Schedule selection follows qualifying-child status whatever the child's
    identification.
12. Before 2023 a qualifying child with no number gives the same dc_eitc as
    one with an ITIN, since IRC 32(m) treats the two alike.
13. In every year, removing a qualifying child's TIN never raises dc_eitc.
"""

import gc
import itertools

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation

YEARS = [2021, 2022, 2023, 2025]
ITIN_START = 2023

# Dependent kinds: (age, disabled, parent, grandparent). A kind of None has no
# dependent. "child" takes the drawn child age.
KINDS = {
    "none": None,
    "child": ("draw", False, False, False),
    "disabled_adult_child": (30, True, False, False),
    "adult_child": (30, False, False, False),
    "disabled_parent": (75, True, True, False),
    "parent": (75, False, True, False),
    "disabled_grandparent": (90, True, False, True),
    "grandparent": (90, False, False, True),
}
QUALIFYING_CHILD_KINDS = ["child", "disabled_adult_child"]
ASCENDANT_KINDS = ["disabled_parent", "parent", "disabled_grandparent", "grandparent"]
# (ssn_card_type, has_tin)
IDS = {"ssn": ("CITIZEN", True), "itin": ("NONE", True), "none": ("NONE", False)}
STATES = ["DC", "CA", "CO", "IL", "MN", "WA", "TX"]
CREDITS = [
    "eitc",
    "dc_eitc",
    "ca_eitc",
    "co_eitc",
    "il_eitc",
    "mn_child_and_working_families_credits",
    "wa_working_families_tax_credit",
]

household_draw = st.fixed_dictionaries(
    {
        "earnings": st.integers(0, 60_000),
        "interest": st.one_of(st.just(0), st.integers(0, 15_000)),
        "head_age": st.integers(19, 70),
        "child_age": st.integers(0, 18),
    }
)


def build(draw, rows, system=None):
    """One tax unit per row; returns the simulation and row metadata."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    dependent_index = []
    person_count = 0
    for i, (kind, dep_id, filer_id, state) in enumerate(rows):
        card, has_tin = IDS[filer_id]
        head = f"h{i}"
        situation["people"][head] = {
            "age": {y: draw["head_age"] for y in YEARS},
            "is_tax_unit_head": {y: True for y in YEARS},
            "employment_income": {y: draw["earnings"] for y in YEARS},
            "taxable_interest_income": {y: draw["interest"] for y in YEARS},
            "ssn_card_type": {y: card for y in YEARS},
            "has_tin": {y: has_tin for y in YEARS},
        }
        members = [head]
        person_count += 1
        spec = KINDS[kind]
        if spec is None:
            dependent_index.append(-1)
        else:
            age, disabled, parent, grandparent = spec
            age = draw["child_age"] if age == "draw" else age
            dep_card, dep_has_tin = IDS[dep_id]
            dependent = f"d{i}"
            situation["people"][dependent] = {
                "age": {y: age for y in YEARS},
                "is_tax_unit_dependent": {y: True for y in YEARS},
                "is_tax_unit_spouse": {y: False for y in YEARS},
                "is_permanently_and_totally_disabled": {y: disabled for y in YEARS},
                "is_parent_of_filer_or_spouse": {y: parent for y in YEARS},
                "is_grandparent_of_filer_or_spouse": {y: grandparent for y in YEARS},
                "ssn_card_type": {y: dep_card for y in YEARS},
                "has_tin": {y: dep_has_tin for y in YEARS},
            }
            members.append(dependent)
            dependent_index.append(person_count)
            person_count += 1
        situation["tax_units"][f"t{i}"] = {"members": members}
        situation["households"][f"hh{i}"] = {
            "members": members,
            "state_code": {y: state for y in YEARS},
        }
    simulation = Simulation(situation=situation, tax_benefit_system=system)
    return simulation, np.array(dependent_index)


def index_rows(rows):
    return {row: i for i, row in enumerate(rows)}


DC_ROWS = [
    (kind, dep_id, filer_id, "DC")
    for kind, dep_id, filer_id in itertools.product(KINDS, IDS, ["ssn", "itin"])
    if not (kind == "none" and dep_id != "ssn")
]
STATE_ROWS = [
    (kind, dep_id, filer_id, state)
    for kind, dep_id, filer_id, state in itertools.product(
        ASCENDANT_KINDS + ["adult_child"], ["ssn", "itin"], ["ssn", "itin"], STATES
    )
]


@pytest.fixture(scope="module")
def tin_rule_off_system():
    """The tax-benefit system with qualifying_child_tin_required off.

    Built once for this module and only read. It is released when the module
    finishes, so the rest of the pytest process does not keep a second full
    system resident.
    """
    reform = Reform.from_dict(
        {
            "gov.states.dc.tax.income.credits.eitc.qualifying_child_tin_required": {
                "2015-01-01.2100-12-31": False
            }
        },
        country_id="us",
    )
    yield CountryTaxBenefitSystem(reform=reform)
    gc.collect()


SETTINGS = settings(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)


@SETTINGS
@given(draw=household_draw)
def test_dc_eitc_invariants(draw):
    sim, dependent_index = build(draw, DC_ROWS)
    row = index_rows(DC_ROWS)
    for year in YEARS:
        with_child = sim.calculate("dc_eitc_with_qualifying_child", year)
        without = sim.calculate("dc_eitc_without_qualifying_child", year)
        dc_eitc = sim.calculate("dc_eitc", year)
        has_child = sim.calculate("dc_eitc_has_qualifying_child", year)
        federal = sim.calculate("eitc", year)
        qualifying = sim.calculate("is_eitc_qualifying_child", year)
        match = sim.tax_benefit_system.parameters(
            f"{year}-01-01"
        ).gov.states.dc.tax.income.credits.eitc.with_children.match
        context = f"year {year}, draw {draw}"

        # 1. Ascendants are never qualifying children.
        for (kind, *_), i in row.items():
            if kind in ASCENDANT_KINDS:
                assert not qualifying[dependent_index[i]], (kind, context)
                assert not has_child[i], (kind, context)
        # 9. An ITIN child routes like a Social Security number child; a
        # qualifying child with neither number leaves the unit where the same
        # filer with no dependent would be.
        for kind, filer_id in itertools.product(
            QUALIFYING_CHILD_KINDS, ["ssn", "itin"]
        ):
            ssn = row[(kind, "ssn", filer_id, "DC")]
            itin = row[(kind, "itin", filer_id, "DC")]
            no_tin = row[(kind, "none", filer_id, "DC")]
            alone = row[("none", "ssn", filer_id, "DC")]
            assert qualifying[dependent_index[no_tin]], (kind, context)
            assert has_child[ssn] and has_child[itin], (kind, context)
            assert not has_child[no_tin] and not has_child[alone], (kind, context)
            assert np.isclose(dc_eitc[no_tin], dc_eitc[alone]), (kind, context)

        # 4 and 5. Branch structure.
        assert np.all(with_child >= 0) and np.all(without >= 0), context
        assert np.all(with_child * without == 0), context
        assert np.all(with_child[~has_child] == 0), context
        assert np.all(without[has_child] == 0), context
        assert np.allclose(dc_eitc, np.where(has_child, with_child, without)), context
        assert np.allclose(dc_eitc, np.maximum(with_child, without)), context

        # 3. Disability never moves a unit off the with-child schedule.
        for dep_id, filer_id in itertools.product(IDS, ["ssn", "itin"]):
            disabled = row[("disabled_adult_child", dep_id, filer_id, "DC")]
            plain = row[("adult_child", dep_id, filer_id, "DC")]
            assert has_child[disabled] >= has_child[plain], context

        if year < ITIN_START:
            # 6. Differential check against the federal credit.
            assert np.allclose(with_child, np.where(has_child, match * federal, 0)), (
                context
            )
            # 7. No ITIN path before 2023.
            itin_filer = np.array([r[2] == "itin" for r in DC_ROWS])
            assert np.all(dc_eitc[itin_filer] == 0), context
            for kind, filer_id in itertools.product(
                QUALIFYING_CHILD_KINDS, ["ssn", "itin"]
            ):
                ssn = row[(kind, "ssn", filer_id, "DC")]
                itin = row[(kind, "itin", filer_id, "DC")]
                assert dc_eitc[itin] <= dc_eitc[ssn] + 1e-6, (kind, context)
        else:
            # 8. ITIN invariance from 2023.
            for kind, filer_id in itertools.product(
                QUALIFYING_CHILD_KINDS, ["ssn", "itin"]
            ):
                ssn = row[(kind, "ssn", filer_id, "DC")]
                itin = row[(kind, "itin", filer_id, "DC")]
                assert np.isclose(dc_eitc[itin], dc_eitc[ssn]), (kind, context)
            # 10. From 2023, removing a qualifying child's TIN never raises
            # the credit.
            assert_no_tin_never_raises(dc_eitc, row, context)


def assert_no_tin_never_raises(dc_eitc, row, context):
    for kind, filer_id in itertools.product(QUALIFYING_CHILD_KINDS, ["ssn", "itin"]):
        for dep_id in ["ssn", "itin"]:
            with_tin = row[(kind, dep_id, filer_id, "DC")]
            no_tin = row[(kind, "none", filer_id, "DC")]
            assert dc_eitc[no_tin] <= dc_eitc[with_tin] + 1e-6, (
                kind,
                dep_id,
                filer_id,
                context,
            )


@SETTINGS
@given(draw=household_draw)
def test_dc_eitc_without_tin_rule(tin_rule_off_system, draw):
    sim, dependent_index = build(draw, DC_ROWS, system=tin_rule_off_system)
    row = index_rows(DC_ROWS)
    has_dependent = dependent_index >= 0
    for year in YEARS:
        dc_eitc = sim.calculate("dc_eitc", year)
        has_child = sim.calculate("dc_eitc_has_qualifying_child", year)
        qualifying = sim.calculate("is_eitc_qualifying_child", year)
        context = f"year {year}, draw {draw}, TIN rule off"

        # 11. Routing follows qualifying-child status alone.
        dep_qualifies = np.where(
            has_dependent, qualifying[np.maximum(dependent_index, 0)], False
        )
        assert np.array_equal(has_child, dep_qualifies), context

        # 12. Before 2023 no number is treated like an ITIN.
        if year < ITIN_START:
            for kind, filer_id in itertools.product(
                QUALIFYING_CHILD_KINDS, ["ssn", "itin"]
            ):
                itin = row[(kind, "itin", filer_id, "DC")]
                no_tin = row[(kind, "none", filer_id, "DC")]
                assert np.isclose(dc_eitc[no_tin], dc_eitc[itin]), (kind, context)

        # 13. Removing a qualifying child's TIN never raises the credit.
        assert_no_tin_never_raises(dc_eitc, row, context)


@SETTINGS
@given(draw=household_draw)
def test_relationship_dominates_disability_across_credits(draw):
    sim, dependent_index = build(draw, STATE_ROWS)
    row = index_rows(STATE_ROWS)
    for year in YEARS:
        qualifying = sim.calculate("is_eitc_qualifying_child", year)
        child_count = sim.calculate("eitc_child_count", year)
        values = {credit: sim.calculate(credit, year) for credit in CREDITS}
        context = f"year {year}, draw {draw}"
        for (kind, dep_id, filer_id, state), i in row.items():
            if kind in ASCENDANT_KINDS:
                # 1. Ascendants never qualify, whatever their disability.
                assert not qualifying[dependent_index[i]], (kind, context)
                assert child_count[i] == 0, (kind, context)
        # 2. For an ascendant, disability changes no credit.
        for ascendant in ["parent", "grandparent"]:
            for dep_id, filer_id, state in itertools.product(
                ["ssn", "itin"], ["ssn", "itin"], STATES
            ):
                disabled = row[(f"disabled_{ascendant}", dep_id, filer_id, state)]
                plain = row[(ascendant, dep_id, filer_id, state)]
                for credit, value in values.items():
                    assert np.isclose(value[disabled], value[plain]), (
                        credit,
                        ascendant,
                        dep_id,
                        filer_id,
                        state,
                        context,
                    )
