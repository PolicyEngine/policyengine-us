"""Invariants for estate and trust income in state-built income concepts.

Six states build an income concept from their own source list rather than
from federal AGI, and each state's form puts a beneficiary's estate or trust
income on a line the list already covers:

- Alabama AGI: Form 40, Part I, line 5. Losses do not pass through (Code of
  Ala. § 40-18-25(b)(4) switches off IRC § 642(h)).
- Iowa gross income, tax years 2021 and 2022: IA 1040 line 10, "the income or
  loss from federal Schedule E".
- Mississippi AGI: Form 80-105 line 41, "the income or loss from activities
  reported on Federal Schedule E".
- New Jersey gross income: N.J.S. 54A:5-1(h), a category of its own, so
  N.J.S. 54A:5-2 disregards a net loss.
- New Mexico modified gross income: NMSA 1978 § 7-2-2(L)(15), "undiminished
  by losses".
- Oklahoma gross household income: Forms 538-S and 538-H line 11, "gross
  (positive) income".

Hypothesis draws batches of single filers with wages, interest, partnership
income of either sign and an estate or trust amount of either sign; a seeded
population adds breadth. Each batch runs as one vectorized simulation holding
three copies of every filer in every state: no estate income, the estate
amount, and the same amount entered as rental income instead. For every filer:

1. Signed pass-through (Iowa, Mississippi): the concept moves by exactly the
   estate amount, loss or gain.
2. Floored pass-through (Alabama, New Jersey, New Mexico, Oklahoma): the
   concept moves by exactly max(estate amount, 0), so a loss never lowers it
   and never offsets wages, interest or partnership income.
3. Differential against the existing rental line: the estate amount moves the
   concept exactly as the same amount of rental income does. Every state but
   Alabama treats the two alike for losses too; Alabama passes a rental loss
   through but not an estate or trust loss, so there the two agree only for
   gains.

The identities hold for this income mix. The federal EITC is set to zero
because Oklahoma counts it (Form 538-S line 9) and an estate loss changes it.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# (state, variable, year, whether an estate or trust loss passes through)
CONCEPTS = [
    ("AL", "al_agi", 2025, False),
    ("IA", "ia_gross_income", 2022, True),
    ("MS", "ms_agi", 2025, True),
    ("NJ", "nj_gross_income", 2025, False),
    ("NM", "nm_modified_gross_income", 2025, False),
    ("OK", "ok_gross_income", 2025, False),
]
YEARS = sorted({year for _, _, year, _ in CONCEPTS})
VARIANTS = ("none", "estate", "rental")

amounts = st.one_of(
    st.just(0.0),
    st.integers(-200_000, -1).map(float),
    st.integers(1, 400_000).map(float),
)


@st.composite
def filers(draw):
    return {
        "wages": float(draw(st.integers(0, 300_000))),
        "interest": float(draw(st.integers(0, 40_000))),
        "partnership": float(draw(st.integers(-50_000, 100_000))),
        "estate": draw(amounts),
    }


SEED = 20261010


def _seeded_filers(n=60):
    rng = np.random.default_rng(SEED)
    drawn = [
        {
            "wages": float(rng.integers(0, 300_001)),
            "interest": float(rng.integers(0, 40_001)),
            "partnership": float(rng.integers(-50_000, 100_001)),
            "estate": float(
                rng.choice(
                    [0, rng.integers(-200_000, 0), rng.integers(1, 400_001)],
                    p=[0.1, 0.4, 0.5],
                )
            ),
        }
        for _ in range(n)
    ]
    edges = [
        # Nothing but an estate or trust loss.
        {"wages": 0.0, "interest": 0.0, "partnership": 0.0, "estate": -40_000.0},
        # Nothing but estate or trust income.
        {"wages": 0.0, "interest": 0.0, "partnership": 0.0, "estate": 25_000.0},
        # An estate loss beside partnership income of the same size.
        {"wages": 50_000.0, "interest": 0.0, "partnership": 8_000.0, "estate": -8_000.0},
        # An estate gain beside a partnership loss of the same size.
        {"wages": 50_000.0, "interest": 0.0, "partnership": -8_000.0, "estate": 8_000.0},
    ]  # fmt: skip
    return drawn + edges


def _situation(units):
    def every_year(value):
        return {year: value for year in YEARS}

    people, tax_units, households = {}, {}, {}
    for state, _, _, _ in CONCEPTS:
        for variant in VARIANTS:
            for i, unit in enumerate(units):
                name = f"{state}_{variant}_{i}"
                people[name] = {
                    "age": every_year(45),
                    "employment_income": every_year(unit["wages"]),
                    "taxable_interest_income": every_year(unit["interest"]),
                    "partnership_s_corp_income": every_year(unit["partnership"]),
                    "estate_income": every_year(
                        unit["estate"] if variant == "estate" else 0.0
                    ),
                    "rental_income": every_year(
                        unit["estate"] if variant == "rental" else 0.0
                    ),
                }
                tax_units[name] = {"members": [name], "eitc": every_year(0)}
                households[name] = {
                    "members": [name],
                    "state_code": every_year(state),
                }
    return {"people": people, "tax_units": tax_units, "households": households}


def _check(units):
    sim = Simulation(situation=_situation(units))
    n = len(units)
    estate = np.array([unit["estate"] for unit in units])
    for index, (state, variable, year, loss_passes_through) in enumerate(CONCEPTS):
        # One person per tax unit and household, in insertion order, so a
        # person-level and a tax-unit-level concept index the same way.
        values = np.asarray(sim.calculate(variable, year), dtype=float)
        start = index * len(VARIANTS) * n
        none, with_estate, with_rental = (
            values[start + k * n : start + (k + 1) * n] for k in range(len(VARIANTS))
        )
        expected = estate if loss_passes_through else np.maximum(estate, 0)

        # 1 and 2. Pass-through, signed or floored.
        np.testing.assert_allclose(
            with_estate - none, expected, atol=TOLERANCE, err_msg=f"{state} {variable}"
        )

        # 3. Differential against the rental line. Alabama passes a rental
        # loss through but not an estate or trust loss.
        alike = np.ones(n, dtype=bool) if state != "AL" else estate >= 0
        np.testing.assert_allclose(
            with_estate[alike],
            with_rental[alike],
            atol=TOLERANCE,
            err_msg=f"{state} {variable} against rental income",
        )


@settings(
    max_examples=4,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(filers(), min_size=1, max_size=10))
def test_state_estate_income_invariants(units):
    _check(units)


def test_state_estate_income_invariants_seeded_population():
    _check(_seeded_filers())
