"""Property tests: capital gains in Montana elderly homeowner/renter credit
income are counted without losses.

MCA 15-30-2337(9)(a) defines income as "federal adjusted gross income,
without regard to loss", and 2024 Schedule 2EC line 7 says "do not include
any capital losses". A person's capital gains therefore enter gross household
income as the year's gains without losses. Three losses can hide them:
a short-term loss netted against a long-term gain (or the reverse), the
prior-year long-term capital loss carryover that long_term_capital_gains
already includes, and losses netted against capital gain distributions. The
model counts the gains through three paths (federal AGI and the loss_ald
add-back for filers; dependent_gross_income for tax unit dependents) and
restores what each path nets away.

For a claimant aged 62 or older with a pension, and one other household
member whose capital gains are drawn either as long-term and short-term
parts or as a net capital_gains amount supplied directly, with a carryover
and distributions:

1. Gross household income equals the pension plus the member's gains without
   losses: max(0, long-term + carryover) + max(0, short-term) from the parts,
   or max(0, net + carryover) from a direct net amount, plus distributions.
   This holds whether the member is the claimant's dependent (A), files
   their own return (B), or is the claimant's own gains on the claimant's
   return (C, the claimant alone with the member's capital inputs).
2. The claimant's credit is the same in A and B.

The reference is written from the form, independently of the model. The
model computes in single precision, so comparisons allow one cent or eight
float32 spacings at the case's total, whichever is larger.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2024
PENSION = 20_000
PROPERTY_TAX = 2_000
TOLERANCE = 0.01


def capital_inputs(c=None):
    """Every capital input, set for every person: once capital_gains is an
    input for some people in a simulation, the others get its default (zero),
    not long_term_capital_gains + short_term_capital_gains. A direct net amount
    has no long-term or short-term parts."""
    c = c or dict(direct=True, net=0, carryover=0, distributions=0)
    if c["direct"]:
        long_term, short_term, net = 0, 0, c["net"]
    else:
        long_term, short_term = c["long_term"], c["short_term"]
        net = long_term + short_term
    return {
        "long_term_capital_gains": {YEAR: long_term},
        "short_term_capital_gains": {YEAR: short_term},
        "capital_gains": {YEAR: net},
        "long_term_capital_loss_carryover": {YEAR: c["carryover"]},
        "non_sch_d_capital_gains": {YEAR: c["distributions"]},
    }


def build_situation(cases):
    """Per case, three Montana households: (A) the member is the claimant's
    dependent, (B) the member files their own return and (C) the claimant
    alone, with the member's capital inputs on the claimant's return."""
    people, tax_units, marital_units, households = {}, {}, {}, {}
    for i, c in enumerate(cases):
        for arrangement in "ABC":
            key = f"{arrangement}{i}"
            claimant = f"claimant_{key}"
            people[claimant] = {
                "age": {YEAR: 70},
                "taxable_pension_income": {YEAR: PENSION},
                "real_estate_taxes": {YEAR: PROPERTY_TAX},
                "is_tax_unit_dependent": {YEAR: False},
                **capital_inputs(),
            }
            marital_units[f"marital_unit_{key}"] = {"members": [claimant]}
            if arrangement == "C":
                people[claimant].update(capital_inputs(c))
                tax_units[f"tax_unit_{key}"] = {"members": [claimant]}
                households[f"household_{key}"] = {
                    "members": [claimant],
                    "state_code": {YEAR: "MT"},
                }
                continue
            member = f"member_{key}"
            # Set for everyone: an input for some people gives the others its
            # default, not its formula.
            people[member] = {
                "age": {YEAR: 30},
                "is_tax_unit_dependent": {YEAR: arrangement == "A"},
                **capital_inputs(c),
            }
            marital_units[f"marital_unit_{key}_member"] = {"members": [member]}
            if arrangement == "A":
                tax_units[f"tax_unit_{key}"] = {"members": [claimant, member]}
            else:
                tax_units[f"tax_unit_{key}"] = {"members": [claimant]}
                tax_units[f"tax_unit_{key}_member"] = {"members": [member]}
            households[f"household_{key}"] = {
                "members": [claimant, member],
                "state_code": {YEAR: "MT"},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }


def gains_without_losses(c):
    """Schedule 2EC line 7 (and line 17 for another member): the year's
    capital gains without losses, plus distributions."""
    if c["direct"]:
        gains = max(0, c["net"] + c["carryover"])
    else:
        gains = max(0, c["long_term"] + c["carryover"]) + max(0, c["short_term"])
    return gains + c["distributions"]


def check(cases):
    simulation = Simulation(situation=build_situation(cases))
    income = np.asarray(
        simulation.calculate(
            "mt_elderly_homeowner_or_renter_credit_gross_household_income",
            YEAR,
            map_to="household",
        )
    ).reshape(len(cases), 3)
    credit = np.asarray(
        simulation.calculate(
            "mt_elderly_homeowner_or_renter_credit", YEAR, map_to="household"
        )
    ).reshape(len(cases), 3)
    for i, c in enumerate(cases):
        expected = PENSION + gains_without_losses(c)
        scale = PENSION + sum(
            abs(c[k])
            for k in ["long_term", "short_term", "net", "carryover", "distributions"]
        )
        tol = max(TOLERANCE, 8 * float(np.spacing(np.float32(scale))))
        # 1. Every path counts the gains without losses.
        assert income[i] == pytest.approx([expected] * 3, abs=tol), c
        # 2. The credit does not depend on how the member files.
        assert credit[i, 0] == pytest.approx(credit[i, 1], abs=tol), c
    return income, credit


def test_examples():
    """A 10,000 long-term gain this year with a 4,000 carryover (6,000 net);
    a 4,000 short-term loss against it; and a direct -5,000 net with a 5,000
    carryover, which hides no gain."""
    zero = dict(long_term=0, short_term=0, net=0, carryover=0, distributions=0)
    cases = [
        {**zero, "direct": False, "long_term": 6_000, "carryover": 4_000},
        {**zero, "direct": False, "long_term": 10_000, "short_term": -4_000},
        {**zero, "direct": True, "net": -5_000, "carryover": 5_000},
    ]
    income, credit = check(cases)
    assert income[:, 0].tolist() == pytest.approx([30_000, 30_000, 20_000])
    # (30_000 - 12_600) x 0.05 = 870 and 2_000 - 870 = 1_130; the third case
    # has 20_000: (7_400 x 0.035 = 259), so the 1_150 cap.
    assert credit[:, 0].tolist() == pytest.approx([1_130, 1_130, 1_150], abs=0.01)


try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    SLOW = [hypothesis.HealthCheck.too_slow]
    SIGNED = st.integers(min_value=-30_000, max_value=30_000)
    NONNEGATIVE = st.integers(min_value=0, max_value=20_000)

    @st.composite
    def case(draw):
        return {
            "direct": draw(st.booleans()),
            "long_term": draw(st.one_of(st.just(0), SIGNED)),
            "short_term": draw(st.one_of(st.just(0), SIGNED)),
            "net": draw(st.one_of(st.just(0), SIGNED)),
            "carryover": draw(st.one_of(st.just(0), NONNEGATIVE)),
            "distributions": draw(st.one_of(st.just(0), NONNEGATIVE)),
        }

    @hypothesis.settings(
        max_examples=20, deadline=None, derandomize=True, suppress_health_check=SLOW
    )
    @hypothesis.given(st.lists(case(), min_size=1, max_size=8))
    def test_gains_without_losses(cases):
        check(cases)
