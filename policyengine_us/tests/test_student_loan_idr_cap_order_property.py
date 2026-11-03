"""Hypothesis checks: the IBR and PAYE 10-year cap applies before proration.

34 CFR 685.209(f)(2) and (f)(3) make an Income-Based Repayment or Pay As You
Earn payment the lesser of the income-based amount A = rate x discretionary
income and the borrower's own 10-year standard payment S on their Direct and
FFEL loans. 685.209(g)(1) then multiplies that lesser amount by the balance
share: own Direct / couple's (Direct + FFEL). So, with own Direct d, own FFEL
f and the couple's Direct and FFEL total T:

    P = min(A, S) x d / T

Properties, for generated balances, interest rates, new-borrower status and
discretionary income:

1. Differential: with no spouse debt, P equals min(A x d / (d + f),
   S x d / (d + f)), written here independently of the model.
2. Identity: P equals min(A, S) x d / T, and a borrower whose spouse has no
   eligible debt pays what a single filer pays at the same income.
3. Bound: P <= S x d / (d + f) and P <= A x d / T.
4. Monotonicity: P never falls as income rises, and never rises as the
   spouse's balance rises.

The model's payment also rounds to the cent, applies the small-payment rule
of 685.209(g)(1)(iii) and caps the payment at the Direct Loan balance. That
post-processing is a nondecreasing function of P, so each property is
checked on the model's payment against references passed through the same
post-processing: equalities stay equalities, and bounds and monotonicity
carry through.

Every generated couple is simulated in five variants (as drawn, with more
income, with a larger spouse balance, with no spouse debt, and as a single
filer) in one vectorized simulation per example.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

MONTH = "2026-01"
YEAR = 2026
# Written from the law, not read from the parameter tree.
IBR_RATE = 0.15  # 20 U.S.C. 1098e(b)(1); 685.209(f)(3)(i)
IBR_NEW_BORROWER_RATE = 0.10  # 20 U.S.C. 1098e(e); 685.209(f)(2)(i)
PAYE_RATE = 0.10  # 685.209(f)(2)(i)
STANDARD_MONTHS = 120  # 685.208(b)(1)(i)
STANDARD_MINIMUM = 50  # 685.208(b)(1)(ii)
SMALL_THRESHOLD = 5  # 685.209(g)(1)(iii)(A)
SMALL_MINIMUM = 10  # 685.209(g)(1)(iii)(B)
TOLERANCE = 0.011
VARIANTS = ("base", "more_income", "larger_spouse_balance", "no_spouse_debt")


def standard_payment(balance, annual_rate):
    """10-year level payment on the balance, at least 50, at most the balance."""
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        amortized = balance / STANDARD_MONTHS
    else:
        amortized = (
            balance * monthly_rate / (1 - (1 + monthly_rate) ** -STANDARD_MONTHS)
        )
    return min(max(amortized, STANDARD_MINIMUM), balance)


def post_process(amount, direct_balance):
    """Round to the cent, apply the small-payment rule, cap at the balance."""
    rounded = round(amount, 2)
    if rounded < SMALL_THRESHOLD:
        adjusted = 0
    else:
        adjusted = max(rounded, SMALL_MINIMUM)
    return min(adjusted, direct_balance)


def near_threshold(amount):
    # A reference within a cent of the 5 dollar threshold can round to the
    # other side of it than the model's floating-point result.
    return abs(amount - SMALL_THRESHOLD) < 0.01


borrower = st.fixed_dictionaries(
    {
        "direct": st.integers(1, 150_000),
        "ffel": st.one_of(st.just(0), st.integers(1, 100_000)),
        "rate": st.sampled_from([0, 0.03, 0.055, 0.068, 0.12]),
        "new_borrower": st.booleans(),
    }
)
spouse = st.fixed_dictionaries(
    {
        "direct": st.one_of(st.just(0), st.integers(1, 150_000)),
        "ffel": st.one_of(st.just(0), st.integers(1, 100_000)),
        "rate": st.sampled_from([0, 0.03, 0.055, 0.068, 0.12]),
        "new_borrower": st.booleans(),
    }
)
couple = st.fixed_dictionaries(
    {
        "borrower": borrower,
        "spouse": spouse,
        # Monthly discretionary income, often enough to reach the cap.
        "income": st.one_of(st.integers(0, 2_000), st.integers(0, 15_000)),
        "income_rise": st.integers(1, 5_000),
        "spouse_direct_rise": st.integers(0, 50_000),
        "spouse_ffel_rise": st.integers(0, 50_000),
    }
)


def person_input(name, loans):
    return name, {
        "age": {YEAR: 40},
        "federal_student_loan_balance": {YEAR: loans["direct"]},
        "federal_ffel_loan_balance": {YEAR: loans["ffel"]},
        "federal_student_loan_interest_rate": {YEAR: loans["rate"]},
        "is_income_based_repayment_new_borrower": {YEAR: loans["new_borrower"]},
    }


def build(couples):
    """One situation holding every variant of every couple, in a fixed order."""
    people, tax_units, households, marital_units = {}, {}, {}, {}
    order = []

    def add_unit(key, members, income, filing_status):
        names = []
        for i, loans in enumerate(members):
            name, values = person_input(f"{key}_p{i}", loans)
            people[name] = values
            names.append(name)
            order.append((key, i))
        tax_units[key] = {
            "members": names,
            "filing_status": {YEAR: filing_status},
            "income_based_repayment_discretionary_income": {MONTH: income},
            "pay_as_you_earn_discretionary_income": {MONTH: income},
        }
        households[key] = {"members": names, "state_code": {YEAR: "TX"}}
        marital_units[key] = {"members": names}

    for n, c in enumerate(couples):
        b, s = c["borrower"], c["spouse"]
        add_unit(f"c{n}_base", [b, s], c["income"], "JOINT")
        add_unit(f"c{n}_more_income", [b, s], c["income"] + c["income_rise"], "JOINT")
        larger = dict(
            s,
            direct=s["direct"] + c["spouse_direct_rise"],
            ffel=s["ffel"] + c["spouse_ffel_rise"],
        )
        add_unit(f"c{n}_larger_spouse_balance", [b, larger], c["income"], "JOINT")
        add_unit(
            f"c{n}_no_spouse_debt",
            [b, dict(s, direct=0, ffel=0)],
            c["income"],
            "JOINT",
        )
        add_unit(f"c{n}_single", [b], c["income"], "SINGLE")
    situation = {
        "people": people,
        "tax_units": tax_units,
        "households": households,
        "marital_units": marital_units,
        "spm_units": {k: {"members": v["members"]} for k, v in households.items()},
        "families": {k: {"members": v["members"]} for k, v in households.items()},
    }
    simulation = Simulation(situation=situation)
    results = {}
    for variable in ("income_based_repayment_payment", "pay_as_you_earn_payment"):
        values = simulation.calculate(variable, MONTH)
        results[variable] = {key: float(v) for key, v in zip(order, values)}
    return results


def plan_rate(variable, loans):
    if variable == "pay_as_you_earn_payment":
        return PAYE_RATE
    return IBR_NEW_BORROWER_RATE if loans["new_borrower"] else IBR_RATE


def check(couples):
    results = build(couples)
    problems = []
    for n, c in enumerate(couples):
        b, s = c["borrower"], c["spouse"]
        for variable, paid in results.items():

            def p(variant, i=0):
                return paid[(f"c{n}_{variant}", i)]

            for i, (own, other) in enumerate(((b, s), (s, b))):
                if own["direct"] == 0:
                    if p("base", i) != 0:
                        problems.append(f"{variable} c{n}: no Direct Loans but pays")
                    continue
                d, f = own["direct"], own["ffel"]
                couple_total = d + f + other["direct"] + other["ffel"]
                a = plan_rate(variable, own) * c["income"]
                cap = standard_payment(d + f, own["rate"])
                share = d / couple_total
                # 2. Identity.
                reference = min(a, cap) * share
                if not near_threshold(reference) and (
                    abs(p("base", i) - post_process(reference, d)) > TOLERANCE
                ):
                    problems.append(
                        f"{variable} c{n} spouse {i}: identity {p('base', i)} vs "
                        f"{post_process(reference, d)}"
                    )
                # 3. Bound.
                own_fraction = d / (d + f)
                for bound, label in (
                    (cap * own_fraction, "standard payment x own Direct fraction"),
                    (a * share, "income-based amount x balance share"),
                ):
                    if p("base", i) > post_process(bound, d) + TOLERANCE:
                        problems.append(
                            f"{variable} c{n} spouse {i}: {p('base', i)} above {label}"
                        )
                # 4. Monotonicity in income.
                if p("more_income", i) < p("base", i) - TOLERANCE:
                    problems.append(f"{variable} c{n} spouse {i}: falls with income")
            # The borrower (spouse 0) always has Direct Loans.
            d, f = b["direct"], b["ffel"]
            a = plan_rate(variable, b) * c["income"]
            cap = standard_payment(d + f, b["rate"])
            fraction = d / (d + f)
            # 1. Differential: main's order, which agrees with no spouse debt.
            differential = min(a * fraction, cap * fraction)
            if not near_threshold(differential):
                for variant in ("no_spouse_debt", "single"):
                    if abs(p(variant) - post_process(differential, d)) > TOLERANCE:
                        problems.append(
                            f"{variable} c{n} {variant}: {p(variant)} vs "
                            f"{post_process(differential, d)}"
                        )
            # 2. Identity: no spouse debt pays what a single filer pays.
            if abs(p("no_spouse_debt") - p("single")) > TOLERANCE:
                problems.append(f"{variable} c{n}: joint with no spouse debt != single")
            # 4. Monotonicity in the spouse's balance.
            if p("larger_spouse_balance") > p("base") + TOLERANCE:
                problems.append(f"{variable} c{n}: rises with the spouse's balance")
    assert not problems, "\n".join(problems)


@hypothesis.settings(
    max_examples=10,
    deadline=None,
    # Each example is a simulation of up to 40 people. Shrinking a failure
    # would run hundreds more, so a failing example is reported as drawn.
    phases=[
        hypothesis.Phase.explicit,
        hypothesis.Phase.reuse,
        hypothesis.Phase.generate,
    ],
    suppress_health_check=[
        hypothesis.HealthCheck.too_slow,
        hypothesis.HealthCheck.data_too_large,
    ],
)
@hypothesis.given(st.lists(couple, min_size=1, max_size=8))
def test_cap_before_proration(couples):
    check(couples)


def test_cap_before_proration_hand_case():
    # $30,000 each at 0% and 12%, $600 income-based amount: standard payments
    # 250 and 430.41, so each spouse pays half: 125 and 215.21.
    loans = {"ffel": 0, "new_borrower": False}
    c = {
        "borrower": dict(loans, direct=30_000, rate=0),
        "spouse": dict(loans, direct=30_000, rate=0.12),
        "income": 4_000,
        "income_rise": 1,
        "spouse_direct_rise": 0,
        "spouse_ffel_rise": 0,
    }
    results = build([c])
    paid = results["income_based_repayment_payment"]
    assert paid[("c0_base", 0)] == pytest.approx(125, abs=0.01)
    assert paid[("c0_base", 1)] == pytest.approx(215.21, abs=0.01)
    check([c])
