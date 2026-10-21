"""Invariants for the SALT cap, 26 USC 164(b)(6)(B) and (7).

P.L. 119-21 sec. 70120 sets an applicable limitation amount L ($40,000 for
2025), reduces it by 30% of modified AGI over a threshold T ($500,000 for
2025; half for a separate filer), bars the reduction from taking it below
$10,000, and limits a separate filer to half the result. The 2025 Schedule A
State and Local Tax Deduction Worksheet follows the same order: line 1 is L
for every filing status, line 5 halves only the threshold, line 9 applies the
$10,000 floor, and line 10 halves the result for a separate filer.

With e(M, t) = max(0, M - t), the cap of a filer with modified AGI M is

    C(M) = max(L - 0.3 e(M, T), 10,000)            (other filing statuses)
    S(M) = max(L - 0.3 e(M, T / 2), 10,000) / 2    (married filing separately)

so the statute implies two relations between the separate and joint caps:

1. Shift identity: S(M) = C(M + T / 2) / 2. A separate filer's cap is half
   the joint cap at the MAGI shifted by the separate threshold. It is not
   half the joint cap at twice the MAGI: C(2M) / 2 halves L but applies the
   full 30% rate, which is the order of operations the statute rejects.
2. Split inequality: 2 S(M) >= C(2M), strictly when 0 < e(M, T / 2) <
   (L - 10,000) / 0.3. Two separate returns with equal MAGI keep more cap
   than one joint return at their combined MAGI while the phase-down runs.

Hypothesis draws batches of tax units, each with a filing status, a modified
AGI concentrated near the kinks, an increment, and real estate taxes. Each
batch runs as one vectorized simulation, and again with every AGI raised by
its increment. For every unit:

a. Differential: salt_cap equals the worksheet computed from the statute's
   dollar amounts, not from the model's parameters.
b. Identity and inequality 1 and 2 above, for 2025 through 2027.
c. Bounds: min(cap, floor) <= salt_cap <= cap for the filing status.
d. Monotone and Lipschitz: raising MAGI by d lowers the cap by at least 0
   and at most 30% of d, or 15% of d for a separate filer.
e. Accounting: salt_deduction = min(salt_cap, SALT paid limited to AGI less
   exemptions).

A reform test checks 164(b)(7)(B)(iii): the floor limits the reduction and
never raises a cap set below it.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

TOLERANCE = 0.05  # dollars; the model computes in float32

STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]

# 164(b)(7)(A) and (B)(ii): L and T, with 2027 at 101% of 2026 as
# (7)(A)(iii) and (B)(ii)(III) prescribe (both products are whole dollars).
# 2024 is under the TCJA cap, 164(b)(6)(B) before the amendment, and 2030
# under 164(b)(7)(A)(iv), each with no phase-down.
STATUTE = {
    2024: dict(limit=10_000, threshold=None),
    2025: dict(limit=40_000, threshold=500_000),
    2026: dict(limit=40_400, threshold=505_000),
    2027: dict(limit=40_400 * 1.01, threshold=505_000 * 1.01),
    2030: dict(limit=10_000, threshold=None),
}
PHASE_DOWN_YEARS = [2025, 2026, 2027]
RATE = 0.3
FLOOR = 10_000


def worksheet(year, status, magi):
    """2025 Schedule A State and Local Tax Deduction Worksheet, line 9 or 10."""
    law = STATUTE[year]
    separate = status == "SEPARATE"
    cap = law["limit"]  # Line 1.
    if law["threshold"] is not None:
        threshold = law["threshold"] / 2 if separate else law["threshold"]  # Line 5.
        excess = max(0.0, magi - threshold)  # Line 6.
        cap = max(cap - RATE * excess, FLOOR)  # Lines 7 to 9.
    return cap / 2 if separate else cap  # Line 10.


KINKS = sorted(
    {
        point
        for law in STATUTE.values()
        if law["threshold"] is not None
        for point in [
            law["threshold"] / 2,
            law["threshold"],
            law["threshold"] / 2 + (law["limit"] - FLOOR) / RATE,
            law["threshold"] + (law["limit"] - FLOOR) / RATE,
        ]
    }
)

magis = st.one_of(
    st.integers(0, 1_200_000).map(float),
    st.builds(
        lambda kink, offset: max(0.0, round(kink) + offset),
        st.sampled_from(KINKS),
        st.integers(-2_000, 2_000),
    ),
)
increments = st.one_of(st.just(1.0), st.integers(1, 200_000).map(float))
taxes = st.integers(0, 60_000).map(float)


@st.composite
def units(draw):
    return {
        "status": draw(st.sampled_from(STATUSES)),
        "magi": draw(magis),
        "increment": draw(increments),
        "real_estate_taxes": draw(taxes),
    }


def _situation(rows, year):
    people, tax_units, households = {}, {}, {}
    for i, row in enumerate(rows):
        members = [f"head_{i}"]
        people[f"head_{i}"] = {
            "age": {year: 45},
            "real_estate_taxes": {year: row["real_estate_taxes"]},
        }
        if row["status"] == "JOINT":
            members.append(f"spouse_{i}")
            people[f"spouse_{i}"] = {"age": {year: 45}}
        tax_units[f"tax_unit_{i}"] = {
            "members": members,
            "filing_status": {year: row["status"]},
            "adjusted_gross_income": {year: row["magi"]},
            "state_and_local_sales_or_income_tax": {year: 0},
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
    return {"people": people, "tax_units": tax_units, "households": households}


def _run(rows, year, reform=None):
    sim = Simulation(situation=_situation(rows, year), reform=reform)
    return {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in ["salt_cap", "salt_deduction", "salt", "exemptions"]
    }


def _joint_caps(magis, year):
    rows = [
        {"status": "JOINT", "magi": float(magi), "real_estate_taxes": 0.0}
        for magi in magis
    ]
    return _run(rows, year)["salt_cap"]


def _check(rows, year):
    status = np.array([row["status"] for row in rows])
    separate = status == "SEPARATE"
    magi = np.array([row["magi"] for row in rows])
    increment = np.array([row["increment"] for row in rows])
    base = _run(rows, year)
    raised = _run(
        [{**row, "magi": row["magi"] + row["increment"]} for row in rows], year
    )
    cap = base["salt_cap"]

    # a. Differential against the worksheet.
    expected = np.array([worksheet(year, s, m) for s, m in zip(status, magi)])
    np.testing.assert_allclose(cap, expected, atol=TOLERANCE)

    # c. Bounds.
    law = STATUTE[year]
    top = np.where(separate, law["limit"] / 2, law["limit"])
    bottom = np.where(separate, min(law["limit"], FLOOR) / 2, min(law["limit"], FLOOR))
    assert (cap <= top + TOLERANCE).all()
    assert (cap >= bottom - TOLERANCE).all()

    # d. Monotone and Lipschitz in MAGI.
    drop = cap - raised["salt_cap"]
    slope = np.where(separate, RATE / 2, RATE)
    has_phase_down = law["threshold"] is not None
    assert (drop >= -TOLERANCE).all()
    assert (drop <= slope * increment * has_phase_down + TOLERANCE).all()

    # e. Accounting.
    allowed = np.minimum(base["salt"], np.maximum(0, magi - base["exemptions"]))
    np.testing.assert_allclose(
        base["salt_deduction"], np.minimum(cap, allowed), atol=TOLERANCE
    )

    if year in PHASE_DOWN_YEARS and separate.any():
        # b. Shift identity and split inequality, against joint filers.
        threshold = law["threshold"]
        np.testing.assert_allclose(
            cap[separate],
            _joint_caps(magi[separate] + threshold / 2, year) / 2,
            atol=TOLERANCE,
        )
        joint_double = _joint_caps(2 * magi[separate], year)
        assert (2 * cap[separate] >= joint_double - TOLERANCE).all()
        excess = np.maximum(0, magi[separate] - threshold / 2)
        running = (excess > 0) & (excess < (law["limit"] - FLOOR) / RATE)
        assert (2 * cap[separate][running] > joint_double[running] + TOLERANCE).all()


# Each example is one batch, so a few examples cover many units.
SETTINGS = dict(
    max_examples=10,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(sorted(STATUTE)), st.lists(units(), min_size=5, max_size=40))
def test_salt_cap_invariants(year, rows):
    _check(rows, year)


@pytest.mark.parametrize("year", sorted(STATUTE))
def test_salt_cap_grid(year):
    # Every filing status on a $5,000 MAGI grid through the last kink.
    rows = [
        {
            "status": status,
            "magi": float(magi),
            "increment": 2_500.0,
            "real_estate_taxes": 50_000.0,
        }
        for status in STATUSES
        for magi in range(0, 700_001, 5_000)
    ]
    _check(rows, year)


def test_floor_never_raises_a_lower_cap():
    # 164(b)(7)(B)(iii) bars the reduction from taking the applicable
    # limitation amount below $10,000; it does not lift a smaller amount.
    p = "gov.irs.deductions.itemized.salt_and_real_estate.cap"
    reform = Reform.from_dict(
        {
            f"{p}.JOINT": {"2026": 0},
            f"{p}.SINGLE": {"2026": 6_000},
            f"{p}.SEPARATE": {"2026": 3_000},
        },
        country_id="us",
    )
    rows = [
        {"status": status, "magi": float(magi), "real_estate_taxes": 50_000.0}
        for status in ["JOINT", "SINGLE", "SEPARATE"]
        for magi in [100_000, 300_000, 505_000, 600_000, 1_000_000]
    ]
    cap = _run(rows, 2026, reform=reform)["salt_cap"]
    expected = [
        {"JOINT": 0, "SINGLE": 6_000, "SEPARATE": 3_000}[r["status"]] for r in rows
    ]
    np.testing.assert_allclose(cap, expected, atol=TOLERANCE)
