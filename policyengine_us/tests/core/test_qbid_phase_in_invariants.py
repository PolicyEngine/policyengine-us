"""Invariants for the qualified business income deduction's phase-in.

26 USC 199A(e)(2) sets the threshold at $157,500, indexed under section 1(f)(3)
and rounded under section 1(f)(7) ($50, or $25 for married filing separately),
and doubles it only "in the case of a joint return". Sections 199A(b)(3)(B) and
(d)(3) set the phase-in range at $50,000 ($75,000 from 2026), again doubled only
for a joint return. A qualifying surviving spouse does not file a joint return,
so the IRS lists them under "all other returns" with single and head of
household filers (Rev. Procs. 2019-44 to 2025-32; the 2020 to 2023 Form 8995
instructions name them).

1. The parameters equal the amounts the IRS published for 2018 to 2026, and in
   every year through 2035 a surviving spouse and a head of household get the
   single amounts, a joint return gets twice them, and the thresholds are
   multiples of the 1(f)(7) rounding interval.
2. For drawn businesses on a grid of taxable incomes around every filing
   status's threshold and the end of its phase-in range, run as one vectorized
   simulation per batch:
   a. A surviving spouse's and a head of household's per-person deduction and
      tax unit deduction equal a single filer's.
   b. Without SSTB losses, the per-person deduction never rises with taxable
      income. An SSTB loss is an intended exception: 199A(d)(3)(A)(ii) counts
      only the applicable percentage of SSTB "income, gain, deduction, or
      loss", so less of the loss offsets other QBI as income rises. A 2025
      single filer with $100,000 of non-SSTB QBI, ample W-2 wages and a
      $50,000 SSTB loss gets $10,000 at the threshold and $20,000 past the
      phase-in range.
   c. For a person with one kind of business (non-SSTB or SSTB) and no losses,
      the per-person deduction matches Form 8995-A Part III and Schedule A,
      recomputed in numpy from the IRS table rather than the parameters.
   d. The per-person deduction is never negative and never above 20% of
      positive QBI plus 20% of positive REIT and PTP income.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

TOLERANCE = 0.01  # dollars

STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]

# Threshold amounts (all other returns, joint, married filing separately) and
# phase-in ranges (all other and separate, joint): the statute for 2018 and
# Rev. Procs. 2018-57 3.27, 2019-44 3.27, 2020-45 3.27, 2021-45 3.27,
# 2022-38 3.27, 2023-34 3.27, 2024-40 3.27 and 2025-32 4.26 for 2019 to 2026.
IRS = {
    2018: (157_500, 315_000, 157_500, 50_000, 100_000),
    2019: (160_700, 321_400, 160_725, 50_000, 100_000),
    2020: (163_300, 326_600, 163_300, 50_000, 100_000),
    2021: (164_900, 329_800, 164_925, 50_000, 100_000),
    2022: (170_050, 340_100, 170_050, 50_000, 100_000),
    2023: (182_100, 364_200, 182_100, 50_000, 100_000),
    2024: (191_950, 383_900, 191_950, 50_000, 100_000),
    2025: (197_300, 394_600, 197_300, 50_000, 100_000),
    2026: (201_750, 403_500, 201_775, 75_000, 150_000),
}


def _irs(year, status):
    other, joint, separate, length, joint_length = IRS[year]
    if status == "JOINT":
        return joint, joint_length
    if status == "SEPARATE":
        return separate, length
    return other, length


PHASE_OUT = {
    year: system.parameters(f"{year}-01-01").gov.irs.deductions.qbi.phase_out
    for year in range(2018, 2036)
}


def test_phase_out_parameters_match_the_irs_tables():
    for year in IRS:
        p = PHASE_OUT[year]
        for status in STATUSES:
            assert (p.start[status], p.length[status]) == _irs(year, status), (
                year,
                status,
            )


def test_phase_out_parameters_keep_the_statutory_relations():
    for year, p in PHASE_OUT.items():
        start = {s: p.start[s] for s in STATUSES}
        length = {s: p.length[s] for s in STATUSES}
        for status in ["HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]:
            assert start[status] == start["SINGLE"], (year, status)
            assert length[status] == length["SINGLE"], (year, status)
        assert start["JOINT"] == 2 * start["SINGLE"], year
        assert length["JOINT"] == 2 * length["SINGLE"], year
        assert length["SEPARATE"] == length["SINGLE"], year
        assert start["SINGLE"] % 50 == 0, year
        assert start["SEPARATE"] % 25 == 0, year


money = st.integers(0, 300_000).map(float)


def _maybe(strategy):
    return st.one_of(st.just(0.0), strategy)


@st.composite
def businesses(draw):
    w2_wages = draw(_maybe(money))
    ubia = draw(_maybe(st.integers(0, 2_000_000).map(float)))
    return {
        "qualified_business_income": draw(
            _maybe(st.integers(-50_000, 400_000).map(float))
        ),
        "sstb_qualified_business_income": draw(_maybe(money)),
        "w2_wages_from_qualified_business": w2_wages,
        "sstb_w2_wages_from_qualified_business": draw(
            st.floats(0, 1).map(lambda share: float(round(share * w2_wages)))
        ),
        "unadjusted_basis_qualified_property": ubia,
        "sstb_unadjusted_basis_qualified_property": draw(
            st.floats(0, 1).map(lambda share: float(round(share * ubia)))
        ),
        "qualified_reit_and_ptp_income": draw(
            _maybe(st.integers(-5_000, 30_000).map(float))
        ),
    }


def _income_grid(year):
    """Taxable incomes at and around every status's threshold and range end."""
    p = PHASE_OUT[year]
    points = {0.0}
    for status in STATUSES:
        start, length = p.start[status], p.length[status]
        for edge in [start, start + length / 2, start + length]:
            points.update([edge - 1, edge, edge + 1])
        points.add(start + 2 * length)
    return sorted(points)


def _situation(batch, year, incomes):
    people, tax_units, households = {}, {}, {}
    rows = []
    for b, business in enumerate(batch):
        for status in STATUSES:
            for i, income in enumerate(incomes):
                name = f"{b}_{status}_{i}"
                people[name] = {
                    "age": {year: 45},
                    "is_tax_unit_head": {year: True},
                    "is_tax_unit_spouse": {year: False},
                    "is_tax_unit_dependent": {year: False},
                    "business_is_sstb": {year: False},
                    **{k: {year: v} for k, v in business.items()},
                }
                tax_units[f"tu_{name}"] = {
                    "members": [name],
                    "filing_status": {year: status},
                    "taxable_income_less_qbid": {year: income},
                    "section_199a_net_capital_gain": {year: 0.0},
                }
                households[f"hh_{name}"] = {
                    "members": [name],
                    "state_code": {year: "TX"},
                }
                rows.append((b, status, i))
    situation = {"people": people, "tax_units": tax_units, "households": households}
    return situation, rows


def _reference(business, year, status, income):
    """Form 8995-A Part III and Schedule A for one kind of business, no losses."""
    start, length = _irs(year, status)
    rate = 0.2
    reit = rate * max(0.0, business["qualified_reit_and_ptp_income"])
    non_sstb = business["qualified_business_income"]
    sstb = business["sstb_qualified_business_income"]
    w2 = business["w2_wages_from_qualified_business"]
    ubia = business["unadjusted_basis_qualified_property"]
    reduction = min(1.0, max(0.0, income - start) / length)
    applicable = 1 - reduction if sstb > 0 else 1.0
    qbi = (sstb if sstb > 0 else non_sstb) * applicable
    cap = max(0.5 * w2, 0.25 * w2 + 0.025 * ubia) * applicable
    tentative = rate * qbi
    if cap >= tentative:
        return tentative + reit
    return max(cap, tentative - reduction * (tentative - cap)) + reit


def _check(batch, year):
    incomes = _income_grid(year)
    situation, rows = _situation(batch, year, incomes)
    sim = Simulation(situation=situation)
    qbid = np.asarray(sim.calculate("qbid_amount", year), dtype=float)
    deduction = np.asarray(
        sim.calculate("qualified_business_income_deduction", year), dtype=float
    )
    shape = (len(batch), len(STATUSES), len(incomes))
    qbid = qbid.reshape(shape)
    deduction = deduction.reshape(shape)
    single = STATUSES.index("SINGLE")

    for b, business in enumerate(batch):
        # a. Surviving spouses and heads of household get the single amounts.
        for status in ["SURVIVING_SPOUSE", "HEAD_OF_HOUSEHOLD"]:
            s = STATUSES.index(status)
            np.testing.assert_allclose(
                qbid[b, s], qbid[b, single], atol=TOLERANCE, err_msg=status
            )
            np.testing.assert_allclose(
                deduction[b, s], deduction[b, single], atol=TOLERANCE, err_msg=status
            )

        # b. Without SSTB losses, the deduction never rises with income.
        assert (np.diff(qbid[b], axis=1) <= TOLERANCE).all(), business

        # c. One kind of business without losses matches Form 8995-A.
        non_sstb = business["qualified_business_income"]
        sstb = business["sstb_qualified_business_income"]
        if year in IRS and non_sstb >= 0 and (non_sstb == 0 or sstb == 0):
            for s, status in enumerate(STATUSES):
                expected = [
                    _reference(business, year, status, income) for income in incomes
                ]
                np.testing.assert_allclose(
                    qbid[b, s], expected, atol=TOLERANCE, err_msg=status
                )

        # d. Bounds.
        ceiling = 0.2 * (
            max(0.0, non_sstb)
            + sstb
            + max(0.0, business["qualified_reit_and_ptp_income"])
        )
        assert (qbid[b] >= -TOLERANCE).all(), business
        assert (qbid[b] <= ceiling + TOLERANCE).all(), business


SETTINGS = dict(
    max_examples=20,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(
    st.lists(businesses(), min_size=2, max_size=5),
    st.sampled_from(range(2018, 2028)),
)
def test_drawn_businesses_through_the_phase_in(batch, year):
    _check(batch, year)


SEED = 20261023


def test_seeded_businesses_every_year():
    rng = np.random.default_rng(SEED)

    def some(low, high, p=0.6):
        return float(round(rng.uniform(low, high))) if rng.random() < p else 0.0

    def business():
        w2_wages = some(0, 300_000)
        ubia = some(0, 2_000_000, 0.4)
        return {
            "qualified_business_income": some(-50_000, 400_000, 0.7),
            "sstb_qualified_business_income": some(0, 300_000, 0.4),
            "w2_wages_from_qualified_business": w2_wages,
            "sstb_w2_wages_from_qualified_business": float(
                round(rng.uniform() * w2_wages)
            ),
            "unadjusted_basis_qualified_property": ubia,
            "sstb_unadjusted_basis_qualified_property": float(
                round(rng.uniform() * ubia)
            ),
            "qualified_reit_and_ptp_income": some(-5_000, 30_000, 0.3),
        }

    for year in range(2018, 2028):
        _check([business() for _ in range(6)], year)
