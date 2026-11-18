"""Student loan interest deduction on a joint return with a claimed spouse.

IRC 221(c) denies the deduction "to an individual" for whom another taxpayer
is allowed a dependency deduction. The bar reaches that individual only: on a
joint return the unclaimed spouse keeps the deduction for their own interest,
under the single return-level cap of IRC 221(b)(1) and the joint phase-out of
IRC 221(b)(2), whose MAGI includes both spouses.

Hypothesis draws batches of joint couples with one unclaimed filer and one
filer who may be claimed. Each couple draws whether the claimable filer is the
head or the spouse, so the checks hold for either claimed filer. Each couple
runs in one vectorized simulation in four variants:

- A: the claimable filer is claimed and has the drawn interest;
- B: the claimable filer is claimed and has no interest;
- C: the claimable filer is not claimed and has no interest;
- D: the claimable filer is not claimed and has the drawn interest.

The checks:

1. The unclaimed filer's deduction is the same in A, B and C: it never
   depends on the claimed filer's own interest, or on whether a filer with no
   interest is claimed.
2. A claimed filer's own interest is never deducted: their deduction is zero
   and the return's total in A is no more than the unclaimed filer's own
   interest.
3. The return's deduction never exceeds the cap, in every variant.

Explicit examples put a claimed filer's income inside the joint phase-out in
both years, with the claimed filer as head and as spouse, so a joint MAGI that
dropped the claimed filer would break check 1 by hundreds of dollars.
"""

import numpy as np
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
VARIANTS = {
    "A": dict(claimed=True, spouse_interest=True),
    "B": dict(claimed=True, spouse_interest=False),
    "C": dict(claimed=False, spouse_interest=False),
    "D": dict(claimed=False, spouse_interest=True),
}

money = st.integers(0, 200_000).map(float)
interest = st.one_of(st.just(0.0), st.integers(1, 4_000).map(float))


@st.composite
def couples(draw):
    return {
        "claimed_role": draw(st.sampled_from(["spouse", "head"])),
        "unclaimed_income": draw(money),
        "claimed_income": draw(st.one_of(st.just(0.0), money)),
        "unclaimed_interest": draw(interest),
        "claimed_interest": draw(interest),
    }


def couple(
    claimed_role,
    unclaimed_income,
    claimed_income,
    unclaimed_interest,
    claimed_interest,
):
    return dict(
        claimed_role=claimed_role,
        unclaimed_income=float(unclaimed_income),
        claimed_income=float(claimed_income),
        unclaimed_interest=float(unclaimed_interest),
        claimed_interest=float(claimed_interest),
    )


# Couples whose claimed filer's income moves the joint phase-out. 2025: start
# $170,000, range $30,000; 2019: start $140,000, range $30,000.
PHASE_OUT_2025 = [
    # Joint MAGI 150,000 + 30,000 = 180,000: 2,500 x (1 - 10/30) = 1,666.67,
    # against 2,500 if the claimed spouse's 30,000 were dropped.
    couple("spouse", 150_000, 30_000, 2_500, 1_000),
    # The same with the head claimed.
    couple("head", 150_000, 30_000, 2_500, 1_000),
    # Joint MAGI 165,000 + 20,000 = 185,000: 2,000 x (1 - 15/30) = 1,000,
    # against 2,000 x (1 - 0) = 2,000 at 165,000.
    couple("spouse", 165_000, 20_000, 2_000, 3_000),
    couple("spouse", 2_000, 0, 1_000, 700),
]
PHASE_OUT_2019 = [
    # Joint MAGI 130,000 + 20,000 = 150,000: 2,000 x (1 - 10/30) = 1,333.33,
    # against 2,000 at 130,000.
    couple("spouse", 130_000, 20_000, 2_000, 500),
    couple("head", 130_000, 20_000, 2_000, 500),
    couple("head", 0, 0, 0, 0),
]


def _situation(units, year):
    people, tax_units, households = {}, {}, {}
    for i, unit in enumerate(units):
        claimed_is_head = unit["claimed_role"] == "head"
        for key, variant in VARIANTS.items():
            unclaimed, claimed = f"unclaimed_{i}_{key}", f"claimed_{i}_{key}"
            people[unclaimed] = {
                "age": {year: 30},
                "employment_income": {year: unit["unclaimed_income"]},
                "student_loan_interest": {year: unit["unclaimed_interest"]},
                "claimed_as_dependent_on_another_return": {year: False},
                "is_tax_unit_head": {year: not claimed_is_head},
                "is_tax_unit_spouse": {year: claimed_is_head},
            }
            claimed_interest = (
                unit["claimed_interest"] if variant["spouse_interest"] else 0.0
            )
            people[claimed] = {
                "age": {year: 22},
                "employment_income": {year: unit["claimed_income"]},
                "student_loan_interest": {year: claimed_interest},
                "claimed_as_dependent_on_another_return": {year: variant["claimed"]},
                "is_tax_unit_head": {year: claimed_is_head},
                "is_tax_unit_spouse": {year: not claimed_is_head},
            }
            members = [unclaimed, claimed]
            tax_units[f"tu_{i}_{key}"] = {
                "members": members,
                "filing_status": {year: "JOINT"},
            }
            households[f"hh_{i}_{key}"] = {
                "members": members,
                "state_code": {year: "TX"},
            }
    return {"people": people, "tax_units": tax_units, "households": households}


def _check(units, year):
    sim = Simulation(situation=_situation(units, year))
    ald = sim.calculate("student_loan_interest_ald", year)
    own = sim.calculate("student_loan_interest", year)
    cap = sim.tax_benefit_system.parameters(
        f"{year}-01-01"
    ).gov.irs.ald.student_loan_interest.cap.JOINT
    n_variants = len(VARIANTS)
    # People are ordered unit by unit, variant by variant, unclaimed filer
    # then claimable filer, whichever of them is the head.
    ald = ald.reshape(len(units), n_variants, 2)
    own = own.reshape(len(units), n_variants, 2)
    a, b, c, d = range(n_variants)
    unclaimed_ald = ald[:, :, 0]

    # 1. The unclaimed filer's deduction ignores the claimed filer.
    np.testing.assert_allclose(unclaimed_ald[:, a], unclaimed_ald[:, b], atol=TOLERANCE)
    np.testing.assert_allclose(unclaimed_ald[:, a], unclaimed_ald[:, c], atol=TOLERANCE)

    # 2. The claimed filer's own interest is never deducted.
    assert (ald[:, [a, b], 1] == 0).all()
    assert (ald[:, a].sum(axis=1) <= own[:, a, 0] + TOLERANCE).all()

    # 3. The return's deduction never exceeds the cap.
    assert (ald.sum(axis=2) <= cap + TOLERANCE).all()
    assert (ald >= 0).all()
    # The claimed filer doesn't change the unclaimed filer's deduction
    # through the shared cap: with the claimable filer's interest, the
    # unclaimed filer's share in D is never above their deduction in A.
    assert (unclaimed_ald[:, d] <= unclaimed_ald[:, a] + TOLERANCE).all()


SETTINGS = dict(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@example(PHASE_OUT_2025, 2025)
@example(PHASE_OUT_2019, 2019)
@given(st.lists(couples(), min_size=10, max_size=30), st.sampled_from([2019, 2025]))
def test_claimed_spouse_invariants(units, year):
    _check(units, year)


def test_crafted_witnesses():
    # A claimed spouse with interest beside an unclaimed head below and in
    # the 2025 joint phase-out ($170,000 start, $30,000 range).
    units = [
        couple("spouse", 2_000, 0, 1_000, 700),
        couple("spouse", 150_000, 30_000, 4_000, 3_000),
    ]
    _check(units, 2025)
