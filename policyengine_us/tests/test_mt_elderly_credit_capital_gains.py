"""Invariant tests: capital gains in Montana elderly homeowner/renter credit
income are counted without losses, however they are supplied.

MCA 15-30-2337(9)(a) defines income as "federal adjusted gross income,
without regard to loss", and 2024 Schedule 2EC line 7 says "do not include
any capital losses". So a person's capital gains enter gross household income
as the year's gains without losses. Three losses can hide them:
- a short-term loss netted against a long-term gain, or the reverse;
- the prior-year long-term capital loss carryover, which
  long_term_capital_gains already includes;
- losses netted against capital gain distributions.

The model counts gains through federal AGI and the loss_ald add-back for
filers, and through dependent_gross_income for tax unit dependents, and
restores what each path nets away.

The gain is a piecewise-linear function of a few amounts. So instead of
random draws, one vectorized simulation covers a grid that reaches every
sign region of the long-term amount plus carryover, the short-term amount,
and a net amount, with and without distributions. It supplies them in three
styles:

- parts: long-term and short-term amounts, with capital_gains set to their
  sum;
- sparse parts: long-term and short-term amounts with capital_gains omitted.
  Because capital_gains is an input for other people in the same
  simulation, these people hold its default of zero, not the sum of their
  parts (review round 3 of #10139);
- net: capital_gains alone, without parts.

Each case appears three ways: (A) a household member who is the claimant's
dependent, (B) a member who files their own return, and (C) the claimant
themselves.

1. Gross household income is the claimant's pension plus the gains without
   losses plus distributions. The reference is written from Schedule 2EC
   line 7, independently of the model: with parts,
   max(0, long-term + carryover) + max(0, short-term); without them,
   max(0, net + carryover).
2. The claimant's credit is the same in A and B.

The model computes in single precision, so comparisons allow one cent or
eight float32 spacings at the case's total, whichever is larger.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2024
PENSION = 20_000
PROPERTY_TAX = 2_000
TOLERANCE = 0.01

LONG_TERM = [-12_000, -3_000, 0, 4_000, 11_000]
SHORT_TERM = [-7_000, 0, 2_000, 9_000]
NET = [-9_000, -2_500, 0, 3_000, 14_000]
CARRYOVER = [0, 2_500, 15_000]
DISTRIBUTIONS = [0, 4_000]


def grid():
    cases = []
    for style in ["parts", "sparse"]:
        for lt, st, co, dist in itertools.product(
            LONG_TERM, SHORT_TERM, CARRYOVER, DISTRIBUTIONS
        ):
            if lt == 0 and st == 0:
                continue  # no parts: covered by the net style
            cases.append(
                dict(style=style, long_term=lt, short_term=st, net=lt + st)
                | dict(carryover=co, distributions=dist)
            )
    for net, co, dist in itertools.product(NET, CARRYOVER, DISTRIBUTIONS):
        cases.append(
            dict(style="net", long_term=0, short_term=0, net=net)
            | dict(carryover=co, distributions=dist)
        )
    return cases


def capital_inputs(c):
    inputs = {
        "long_term_capital_loss_carryover": {YEAR: c["carryover"]},
        "non_sch_d_capital_gains": {YEAR: c["distributions"]},
    }
    if c["style"] != "net":
        inputs["long_term_capital_gains"] = {YEAR: c["long_term"]}
        inputs["short_term_capital_gains"] = {YEAR: c["short_term"]}
    if c["style"] != "sparse":
        inputs["capital_gains"] = {YEAR: c["net"]}
    return inputs


NO_CAPITAL = dict(style="parts", long_term=0, short_term=0, net=0) | dict(
    carryover=0, distributions=0
)


def build_situation(cases):
    people, tax_units, marital_units, households = {}, {}, {}, {}
    for i, c in enumerate(cases):
        for arrangement in "ABC":
            key = f"{arrangement}{i}"
            claimant = f"claimant_{key}"
            people[claimant] = {
                "age": {YEAR: 70},
                "taxable_pension_income": {YEAR: PENSION},
                "real_estate_taxes": {YEAR: PROPERTY_TAX},
                # Set for everyone: an input for some people gives the others
                # its default, not its formula.
                "is_tax_unit_dependent": {YEAR: False},
                **capital_inputs(c if arrangement == "C" else NO_CAPITAL),
            }
            marital_units[f"marital_unit_{key}"] = {"members": [claimant]}
            members = [claimant]
            if arrangement == "C":
                tax_units[f"tax_unit_{key}"] = {"members": [claimant]}
            else:
                member = f"member_{key}"
                people[member] = {
                    "age": {YEAR: 30},
                    "is_tax_unit_dependent": {YEAR: arrangement == "A"},
                    **capital_inputs(c),
                }
                marital_units[f"marital_unit_{key}_member"] = {"members": [member]}
                members.append(member)
                if arrangement == "A":
                    tax_units[f"tax_unit_{key}"] = {"members": members}
                else:
                    tax_units[f"tax_unit_{key}"] = {"members": [claimant]}
                    tax_units[f"tax_unit_{key}_member"] = {"members": [member]}
            households[f"household_{key}"] = {
                "members": members,
                "state_code": {YEAR: "MT"},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }


def gains_without_losses(c):
    """Schedule 2EC line 7 (line 17 for another member) plus distributions."""
    if c["style"] == "net":
        gains = max(0, c["net"] + c["carryover"])
    else:
        gains = max(0, c["long_term"] + c["carryover"]) + max(0, c["short_term"])
    return gains + c["distributions"]


@pytest.fixture(scope="module")
def results():
    cases = grid()
    simulation = Simulation(situation=build_situation(cases))
    shape = (len(cases), 3)
    income = np.asarray(
        simulation.calculate(
            "mt_elderly_homeowner_or_renter_credit_gross_household_income",
            YEAR,
            map_to="household",
        )
    ).reshape(shape)
    credit = np.asarray(
        simulation.calculate(
            "mt_elderly_homeowner_or_renter_credit", YEAR, map_to="household"
        )
    ).reshape(shape)
    return cases, income, credit


def tolerance(c):
    scale = PENSION + sum(
        abs(c[k]) for k in ["long_term", "short_term", "net", "carryover"]
    )
    scale += c["distributions"]
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(scale))))


def test_gains_count_without_losses_on_every_path(results):
    cases, income, _ = results
    for i, c in enumerate(cases):
        expected = PENSION + gains_without_losses(c)
        assert income[i] == pytest.approx([expected] * 3, abs=tolerance(c)), c


def test_credit_does_not_depend_on_how_the_member_files(results):
    cases, _, credit = results
    for i, c in enumerate(cases):
        assert credit[i, 0] == pytest.approx(credit[i, 1], abs=tolerance(c)), c


def test_hand_checked_cases(results):
    """Two grid cases are checked by hand. A long-term amount of 11,000 that
    already nets a 15,000 carryover, with a 9,000 short-term gain and no net
    supplied (sparse): the year's long-term gain is 26,000, so 20,000 +
    26,000 + 9,000 = 55,000, and the credit is 0 (55,000 is at least
    45,000). A net -2,500 supplied
    directly with a 2,500 carryover: no gain, so 20,000; (20,000 - 12,600) x
    0.035 = 259, and min(2,000 - 259, 1,150) = 1,150."""
    cases, income, credit = results

    def find(**kw):
        return next(i for i, c in enumerate(cases) if kw.items() <= c.items())

    i = find(
        style="sparse",
        long_term=11_000,
        short_term=9_000,
        carryover=15_000,
        distributions=0,
    )
    assert income[i].tolist() == pytest.approx([55_000] * 3)
    assert credit[i].tolist() == pytest.approx([0] * 3)
    j = find(style="net", net=-2_500, carryover=2_500, distributions=0)
    assert income[j].tolist() == pytest.approx([20_000] * 3)
    assert credit[j].tolist() == pytest.approx([1_150] * 3, abs=0.01)
