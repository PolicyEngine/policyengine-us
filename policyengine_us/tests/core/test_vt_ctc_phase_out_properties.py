"""Properties of Vermont's child tax credit phase-out.

32 V.S.A. 5830f(a) gives $1,000 per qualifying child, and 5830f(b) reduces
"the amount of the credit per child", but not below zero, by $20 for each
$1,000, or fraction thereof, of adjusted gross income over $125,000.

Hypothesis draws a year, a number of children and a list of AGIs, with the
phase-out's edges mixed in. Each AGI appears twice in one vectorized
simulation, once with one child and once with the drawn number. For every
AGI:

1. The credit is never below zero and never above $1,000 per child, because
   (b) reduces it "but not below zero" and (a) pays $1,000 per child.
2. The credit never rises with AGI for the same children, because the
   reduction in (b) grows with each $1,000 of AGI over $125,000.
3. n children get n times one child's credit, because (b) reduces each
   child's credit. A single reduction off the total fails this at any AGI
   over $125,000.

The YAML cases for vt_ctc pin the amounts at the edges by hand.
"""

import numpy as np
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

AMOUNT = 1_000  # 5830f(a): "$1,000.00 per qualifying child"
TOLERANCE = 0.01
# The start of the phase-out, the first fraction of $1,000 above it, the last
# $20 of credit per child (AGI $173,001 to $174,000) and the first AGI with
# none, per the 2025 Schedule IN-112 Child Tax Credit Table.
EDGES = [0, 125_000, 125_001, 126_000, 126_001, 150_000, 174_000, 174_001, 175_000]
# 2022 is the credit's first year; the age limit rose from 5 to 6 in 2025.
YEARS = [2022, 2024, 2025, 2026]

agi_values = st.one_of(st.sampled_from(EDGES), st.integers(0, 300_000))


def build_situation(agis, n_children, year):
    """One tax unit with one child and one with n children for each AGI."""
    people, tax_units, households = {}, {}, {}
    for i, agi in enumerate(agis):
        for kids in (1, n_children):
            name = f"unit_{i}_{kids}"
            members = [f"{name}_parent"]
            people[members[0]] = {"age": {year: 35}}
            for k in range(kids):
                members.append(f"{name}_child_{k}")
                # Ages 0 to 5 are within the age limit in every year.
                people[members[-1]] = {"age": {year: k % 6}}
            tax_units[name] = {
                "members": members,
                "adjusted_gross_income": {year: float(agi)},
            }
            households[name] = {"members": members, "state_code": {year: "VT"}}
    return {"people": people, "tax_units": tax_units, "households": households}


@settings(
    max_examples=10,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    year=st.sampled_from(YEARS),
    agis=st.lists(agi_values, min_size=5, max_size=20),
    n_children=st.integers(2, 4),
)
@example(year=2025, agis=EDGES, n_children=2)
@example(year=2022, agis=EDGES, n_children=4)
# No vt_ctc.yaml case covers 2026, so this example checks the per-child
# reduction in a year that file leaves out.
@example(year=2026, agis=EDGES, n_children=3)
def test_vt_ctc_phase_out_properties(year, agis, n_children):
    agis = sorted(agis)
    sim = Simulation(situation=build_situation(agis, n_children, year))
    ctc = np.asarray(sim.calculate("vt_ctc", year), dtype=float).reshape(-1, 2)
    one, many = ctc[:, 0], ctc[:, 1]
    for credit, kids in ((one, 1), (many, n_children)):
        # 1. Never below zero, never above $1,000 per child.
        assert np.all(credit >= 0)
        assert np.all(credit <= AMOUNT * kids + TOLERANCE)
        # 2. Never rises with AGI (the AGIs are sorted).
        assert np.all(np.diff(credit) <= TOLERANCE)
    # 3. The reduction applies to each child's credit.
    np.testing.assert_allclose(many, n_children * one, atol=TOLERANCE)
