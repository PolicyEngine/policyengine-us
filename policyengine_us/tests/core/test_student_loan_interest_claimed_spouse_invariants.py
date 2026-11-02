"""Student loan interest deduction on a joint return with a claimed spouse.

IRC 221(c) denies the deduction "to an individual" for whom another taxpayer
is allowed a dependency deduction. The bar reaches that individual only: on a
joint return the unclaimed spouse keeps the deduction for their own interest,
under the single return-level cap of IRC 221(b)(1) and the joint phase-out of
IRC 221(b)(2), whose MAGI includes both spouses.

Hypothesis draws batches of joint couples whose head is never claimed. Each
couple runs in one vectorized simulation in four variants:

- A: the spouse is claimed and has the drawn interest;
- B: the spouse is claimed and has no interest;
- C: the spouse is not claimed and has no interest;
- D: the spouse is not claimed and has the drawn interest.

The checks:

1. The unclaimed head's deduction is the same in A, B and C: it never depends
   on the claimed spouse's own interest, or on whether a spouse with no
   interest is claimed.
2. A claimed spouse's own interest is never deducted: their deduction is zero
   and the return's total in A is no more than the head's own interest.
3. The return's deduction never exceeds the cap, in every variant.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
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
        "head_income": draw(money),
        "spouse_income": draw(st.one_of(st.just(0.0), money)),
        "head_interest": draw(interest),
        "spouse_interest": draw(interest),
    }


def _situation(units, year):
    people, tax_units, households = {}, {}, {}
    for i, unit in enumerate(units):
        for key, variant in VARIANTS.items():
            head, spouse = f"head_{i}_{key}", f"spouse_{i}_{key}"
            people[head] = {
                "age": {year: 30},
                "employment_income": {year: unit["head_income"]},
                "student_loan_interest": {year: unit["head_interest"]},
                "claimed_as_dependent_on_another_return": {year: False},
                "is_tax_unit_head": {year: True},
                "is_tax_unit_spouse": {year: False},
            }
            spouse_interest = (
                unit["spouse_interest"] if variant["spouse_interest"] else 0.0
            )
            people[spouse] = {
                "age": {year: 22},
                "employment_income": {year: unit["spouse_income"]},
                "student_loan_interest": {year: spouse_interest},
                "claimed_as_dependent_on_another_return": {year: variant["claimed"]},
                "is_tax_unit_head": {year: False},
                "is_tax_unit_spouse": {year: True},
            }
            members = [head, spouse]
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
    ald = sim.calculate("student_loan_interest_ald", year).values
    own = sim.calculate("student_loan_interest", year).values
    cap = sim.tax_benefit_system.parameters(
        f"{year}-01-01"
    ).gov.irs.ald.student_loan_interest.cap.JOINT
    n_variants = len(VARIANTS)
    # People are ordered unit by unit, variant by variant, head then spouse.
    ald = ald.reshape(len(units), n_variants, 2)
    own = own.reshape(len(units), n_variants, 2)
    a, b, c, d = range(n_variants)
    head_ald = ald[:, :, 0]

    # 1. The unclaimed head's deduction ignores the claimed spouse.
    np.testing.assert_allclose(head_ald[:, a], head_ald[:, b], atol=TOLERANCE)
    np.testing.assert_allclose(head_ald[:, a], head_ald[:, c], atol=TOLERANCE)

    # 2. The claimed spouse's own interest is never deducted.
    assert (ald[:, [a, b], 1] == 0).all()
    assert (ald[:, a].sum(axis=1) <= own[:, a, 0] + TOLERANCE).all()

    # 3. The return's deduction never exceeds the cap.
    assert (ald.sum(axis=2) <= cap + TOLERANCE).all()
    assert (ald >= 0).all()
    # The claimed spouse doesn't change the unclaimed spouse's deduction
    # through the shared cap: with the spouse's interest, the head's share
    # in D is never above the head's deduction in A.
    assert (head_ald[:, d] <= head_ald[:, a] + TOLERANCE).all()


SETTINGS = dict(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(couples(), min_size=10, max_size=30), st.sampled_from([2019, 2025]))
def test_claimed_spouse_invariants(units, year):
    _check(units, year)


def test_crafted_witnesses():
    # A claimed spouse with interest beside an unclaimed head below and in
    # the 2025 joint phase-out ($170,000 start, $30,000 range).
    units = [
        dict(
            head_income=2_000,
            spouse_income=0,
            head_interest=1_000,
            spouse_interest=700,
        ),
        dict(
            head_income=150_000,
            spouse_income=30_000,
            head_interest=4_000,
            spouse_interest=3_000,
        ),
    ]
    _check(units, 2025)
