"""Invariants of North Carolina's $20,000 mortgage and property tax limitation.

N.C. Gen. Stat. 105-153.5(a)(2)b caps home mortgage interest plus real estate
taxes at $20,000, "claimed by both spouses combined" when spouses file
separately. Above $20,000 the deductions are "prorated based on the percentage
paid by each spouse", or, "for joint obligations paid from joint accounts",
"based on the income reported by each spouse". Form D-400 Schedule A applies
this as line 4 (the limitation) and line 5 (the smaller of line 3 and line 4).

Spouses filing separately are two tax units linked by a marital unit, so
YAML's single-situation cases cannot cover what this file checks: many mixed
returns in one vectorized simulation (separate couples with and without a
joint account, joint returns, single filers, a lone separate filer, and a
separate return with a dependent), the same returns with the spouses listed
in the other order, and the results under higher payments. Hypothesis draws
batches, and a seeded population of 120 returns adds breadth. Line 3 and AGI
are inputs, so no federal calculation runs. For every return:

1. Differential: lines 4 and 5 equal an independent restatement of the
   statute, with the $20,000 taken from the statute rather than the
   parameter files. Separate filers are spouses only when an explicit marital
   unit pairs them; the paid share is each spouse's line 3 over the couple's;
   the joint-account share is each spouse's federal AGI, not below zero, over
   the couple's, or one half when neither spouse has any.
2. Bounds: 0 <= line 5 <= line 3, and a couple's two lines 5 never exceed
   $20,000. Without a joint account they add up to the smaller of the
   couple's line 3 total and $20,000.
3. Label invariance: listing a couple's spouses in the other order gives each
   spouse the same result.
4. Monotone (without a joint account): raising one spouse's payments never
   lowers that spouse's deduction or the couple's total, and never raises the
   other spouse's deduction. With a joint account the form can lower the
   total: just above $20,000 each spouse gets the smaller of their own line 3
   and their income share of $20,000. That is intended under the Schedule A
   reading and not checked here.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

CAP = 20_000  # G.S. 105-153.5(a)(2)b
TOLERANCE = 0.01  # dollars
YEARS = ["2024", "2026"]

amounts = st.one_of(
    st.just(0.0),
    st.integers(1, 12_000).map(float),
    st.integers(12_000, 45_000).map(float),
)
incomes = st.one_of(
    st.just(0.0),
    st.integers(-30_000, -1).map(float),
    st.integers(1, 300_000).map(float),
)
increases = st.integers(0, 20_000).map(float)
KINDS = ["separate", "joint", "single", "lone_separate", "separate_dependent"]


@st.composite
def returns(draw):
    kind = draw(st.sampled_from(KINDS))
    spouses = 2 if kind in ("separate", "separate_dependent") else 1
    return {
        "kind": kind,
        "line3": [draw(amounts) for _ in range(spouses)],
        "agi": [draw(incomes) for _ in range(spouses)],
        "increase": draw(increases),
        "joint_account": draw(st.booleans()) and spouses == 2,
    }


def _seeded_returns(n=120, seed=20261009):
    rng = np.random.default_rng(seed)
    drawn = []
    for _ in range(n):
        kind = KINDS[rng.integers(len(KINDS))]
        spouses = 2 if kind in ("separate", "separate_dependent") else 1
        drawn.append(
            {
                "kind": kind,
                "line3": [
                    float(rng.choice([0, rng.integers(1, 45_001)]))
                    for _ in range(spouses)
                ],
                "agi": [float(rng.integers(-30_000, 300_001)) for _ in range(spouses)],
                "increase": float(rng.integers(0, 20_001)),
                "joint_account": bool(rng.random() < 0.5) and spouses == 2,
            }
        )
    return drawn


def _situation(drawn, year, *, swap=False, raise_first=False):
    """One tax unit per return, or two for spouses filing separately."""
    people, tax_units, marital_units, households = {}, {}, {}, {}
    rows = []  # (return index, spouse index) per tax unit, in order
    for i, r in enumerate(drawn):
        order = [1, 0] if swap and len(r["line3"]) == 2 else [0, 1]
        line3 = list(r["line3"])
        if raise_first:
            line3[0] += r["increase"]
        names = []
        if r["kind"] == "joint":
            names = [f"r{i}_head", f"r{i}_spouse"]
            people[names[0]] = {"age": {year: 45}}
            people[names[1]] = {"age": {year: 43}}
            tax_units[f"t{i}"] = {
                "members": names,
                "filing_status": {year: "JOINT"},
                "nc_mortgage_and_property_tax_before_limitation": {year: line3[0]},
                "adjusted_gross_income": {year: r["agi"][0]},
            }
            marital_units[f"m{i}"] = {"members": names}
            rows.append((i, 0))
        elif r["kind"] in ("single", "lone_separate"):
            names = [f"r{i}_head"]
            people[names[0]] = {"age": {year: 45}}
            tax_units[f"t{i}"] = {
                "members": names,
                "filing_status": {
                    year: "SINGLE" if r["kind"] == "single" else "SEPARATE"
                },
                "nc_mortgage_and_property_tax_before_limitation": {year: line3[0]},
                "adjusted_gross_income": {year: r["agi"][0]},
            }
            marital_units[f"m{i}"] = {"members": names}
            rows.append((i, 0))
        else:
            couple = []
            for k in order:
                name = f"r{i}_spouse{k}"
                couple.append(name)
                members = [name]
                people[name] = {"age": {year: 45}}
                if r["kind"] == "separate_dependent" and k == 0:
                    child = f"r{i}_child"
                    people[child] = {
                        "age": {year: 10},
                        "is_tax_unit_dependent": {year: True},
                    }
                    members.append(child)
                    marital_units[f"m{i}_child"] = {"members": [child]}
                    names.append(child)
                tax_units[f"t{i}_{k}"] = {
                    "members": members,
                    "filing_status": {year: "SEPARATE"},
                    "nc_mortgage_and_property_tax_before_limitation": {year: line3[k]},
                    "adjusted_gross_income": {year: r["agi"][k]},
                }
                rows.append((i, k))
            marital_units[f"m{i}"] = {
                "members": couple,
                "mortgage_and_real_estate_taxes_paid_from_joint_account": {
                    year: r["joint_account"]
                },
            }
            names += couple
        households[f"h{i}"] = {"members": names, "state_code": {year: "NC"}}
    situation = {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }
    return Simulation(situation=situation), rows


def _expected(drawn, raise_first=False):
    """Lines 4 and 5 per (return, spouse), restated from the statute."""
    limitation, deduction = {}, {}
    for i, r in enumerate(drawn):
        line3 = list(r["line3"])
        if raise_first:
            line3[0] += r["increase"]
        if len(line3) == 1:
            limitation[i, 0] = CAP
            deduction[i, 0] = min(line3[0], CAP)
            continue
        combined = sum(line3)
        if combined <= CAP:
            shares = None
        elif r["joint_account"]:
            income = [max(a, 0) for a in r["agi"]]
            total = sum(income)
            shares = [a / total for a in income] if total > 0 else [0.5, 0.5]
        else:
            shares = [a / combined for a in line3]
        for k in range(2):
            limitation[i, k] = CAP if shares is None else CAP * shares[k]
            deduction[i, k] = min(line3[k], limitation[i, k])
    return limitation, deduction


def _results(drawn, year, **kwargs):
    simulation, rows = _situation(drawn, year, **kwargs)
    line4 = simulation.calculate("nc_mortgage_and_property_tax_limitation", year)
    line5 = simulation.calculate("nc_mortgage_and_property_tax_deduction", year)
    return (
        {row: float(v) for row, v in zip(rows, line4)},
        {row: float(v) for row, v in zip(rows, line5)},
    )


def _check(drawn, year):
    line3 = {(i, k): a for i, r in enumerate(drawn) for k, a in enumerate(r["line3"])}
    expected4, expected5 = _expected(drawn)
    line4, line5 = _results(drawn, year)

    # 1. Differential against the restated statute.
    for row in expected4:
        assert abs(line4[row] - expected4[row]) < TOLERANCE, (row, drawn[row[0]])
        assert abs(line5[row] - expected5[row]) < TOLERANCE, (row, drawn[row[0]])

    # 2. Bounds, and the couple's total.
    for row, value in line5.items():
        assert -TOLERANCE < value < line3[row] + TOLERANCE
    for i, r in enumerate(drawn):
        if len(r["line3"]) == 2:
            total = line5[i, 0] + line5[i, 1]
            assert total < CAP + TOLERANCE
            if not r["joint_account"]:
                assert abs(total - min(sum(r["line3"]), CAP)) < TOLERANCE

    # 3. The order in which the spouses are listed does not matter.
    swapped4, swapped5 = _results(drawn, year, swap=True)
    for row in line5:
        assert abs(swapped4[row] - line4[row]) < TOLERANCE
        assert abs(swapped5[row] - line5[row]) < TOLERANCE

    # 4. Paying more never lowers the payer's deduction or the couple's total
    # without a joint account.
    raised4, raised5 = _results(drawn, year, raise_first=True)
    expected_raised4, expected_raised5 = _expected(drawn, raise_first=True)
    for row in expected_raised5:
        assert abs(raised4[row] - expected_raised4[row]) < TOLERANCE
        assert abs(raised5[row] - expected_raised5[row]) < TOLERANCE
    for i, r in enumerate(drawn):
        if len(r["line3"]) == 2 and not r["joint_account"]:
            assert raised5[i, 0] > line5[i, 0] - TOLERANCE
            assert raised5[i, 1] < line5[i, 1] + TOLERANCE
            assert raised5[i, 0] + raised5[i, 1] > line5[i, 0] + line5[i, 1] - TOLERANCE


@settings(
    max_examples=6,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(drawn=st.lists(returns(), min_size=5, max_size=25), year=st.sampled_from(YEARS))
def test_nc_mortgage_and_property_tax_limitation_invariants(drawn, year):
    _check(drawn, year)


def test_nc_mortgage_and_property_tax_limitation_seeded_population():
    for year in YEARS:
        _check(_seeded_returns(), year)
