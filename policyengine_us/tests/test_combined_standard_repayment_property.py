"""Hypothesis checks: one standard plan minimum per borrower.

34 CFR 685.208(b)(1) puts Direct Subsidized, Unsubsidized and PLUS loans on
one standard plan, and (b)(1)(ii) sets its $50 minimum on the borrower's
payments. combined_standard_repayment_payment adds the Direct and parent PLUS
level payments before one minimum applies, unless the parent PLUS balance is
a Direct Consolidation Loan under 685.208(b)(2), a separate plan with its own
minimum. With D the Direct variable (standard_repayment_payment), P the parent
PLUS variable (parent_plus_standard_repayment_payment) and C the combined
payment, for generated balances, rates and consolidation flags:

1. Bound: max(D, P) <= C <= D + P, and C <= the total balance.
2. Agreement: C = D + P where both level payments reach the minimum, and
   where the parent PLUS loan is consolidated.
3. One loan type: with one balance zero, C equals the other variable.
4. Monotonicity: C never falls as either balance rises, while the
   consolidation loan's repayment period holds still.
5. Differential: where the parent PLUS loan is not consolidated, C equals
   min(max(Direct level payment + parent PLUS level payment, 50), total
   balance), written here independently of the model. The first four hold
   for D + P too, so this one is what catches a minimum on each loan type.

Each generated borrower is simulated in five variants (as drawn, with a larger
Direct balance, with a larger parent PLUS balance, with no Direct Loans and
with no parent PLUS loans) in one vectorized simulation per example.
"""

import pytest

from policyengine_us import Simulation

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

MONTH = "2026-01"
YEAR = 2026
# Written from the law, not read from the parameter tree.
STANDARD_MONTHS = 120  # 685.208(b)(1)(i)
STANDARD_MINIMUM = 50  # 685.208(b)(1)(ii)
# 685.208(b)(2)(iii): years by the consolidation loan plus other education
# loans, counted up to the consolidation loan's amount.
CONSOLIDATION_TIERS = ((60_000, 30), (40_000, 25), (20_000, 20), (10_000, 15))
CONSOLIDATION_TIERS += ((7_500, 12), (0, 10))
TOLERANCE = 0.011


def amortized(balance, annual_rate, months):
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return balance / months
    return balance * monthly_rate / (1 - (1 + monthly_rate) ** -months)


def consolidation_years(loans):
    if not loans["consolidated"]:
        return 10
    total = loans["parent_plus"] + min(
        loans["direct"] + loans["ffel"], loans["parent_plus"]
    )
    return next(years for floor, years in CONSOLIDATION_TIERS if total >= floor)


borrower = st.fixed_dictionaries(
    {
        "direct": st.one_of(st.just(0), st.integers(1, 6_000), st.integers(1, 80_000)),
        "parent_plus": st.one_of(
            st.just(0), st.integers(1, 6_000), st.integers(1, 80_000)
        ),
        "ffel": st.one_of(st.just(0), st.integers(1, 30_000)),
        "rate": st.sampled_from([0, 0.03, 0.06, 0.08]),
        "consolidated": st.booleans(),
        "new_loan": st.sampled_from([False, False, False, True]),
        "direct_rise": st.integers(1, 20_000),
        "parent_plus_rise": st.integers(1, 20_000),
    }
)


def variants(loans):
    return {
        "base": loans,
        "direct_rise": dict(loans, direct=loans["direct"] + loans["direct_rise"]),
        "parent_plus_rise": dict(
            loans, parent_plus=loans["parent_plus"] + loans["parent_plus_rise"]
        ),
        "no_direct": dict(loans, direct=0),
        "no_parent_plus": dict(loans, parent_plus=0),
    }


def build(borrowers):
    """One situation holding every variant of every borrower."""
    people, tax_units, households = {}, {}, {}
    order = []
    for n, loans in enumerate(borrowers):
        for variant, values in variants(loans).items():
            name = f"b{n}_{variant}"
            people[name] = {
                "age": {YEAR: 50},
                "federal_student_loan_balance": {YEAR: values["direct"]},
                "federal_parent_plus_loan_balance": {YEAR: values["parent_plus"]},
                "federal_ffel_loan_balance": {YEAR: values["ffel"]},
                "federal_student_loan_interest_rate": {YEAR: values["rate"]},
                "federal_parent_plus_loan_is_consolidated": {
                    YEAR: values["consolidated"]
                },
                "has_federal_student_loan_made_on_or_after_2026_07_01": {
                    YEAR: values["new_loan"]
                },
            }
            tax_units[name] = {
                "members": [name],
                "filing_status": {YEAR: "SINGLE"},
            }
            households[name] = {"members": [name], "state_code": {YEAR: "OH"}}
            order.append((n, variant))
    situation = {
        "people": people,
        "tax_units": tax_units,
        "households": households,
        "marital_units": {k: {"members": v["members"]} for k, v in households.items()},
        "spm_units": {k: {"members": v["members"]} for k, v in households.items()},
        "families": {k: {"members": v["members"]} for k, v in households.items()},
    }
    simulation = Simulation(situation=situation)
    results = {}
    for variable in (
        "standard_repayment_payment",
        "parent_plus_standard_repayment_payment",
        "combined_standard_repayment_payment",
    ):
        values = simulation.calculate(variable, MONTH)
        results[variable] = {key: float(v) for key, v in zip(order, values)}
    return results


def check(borrowers):
    results = build(borrowers)
    problems = []
    for n, loans in enumerate(borrowers):
        cases = variants(loans)

        def get(variable, variant):
            return results[variable][(n, variant)]

        for variant, values in cases.items():
            d = get("standard_repayment_payment", variant)
            p = get("parent_plus_standard_repayment_payment", variant)
            c = get("combined_standard_repayment_payment", variant)
            label = f"b{n} {variant} {values}: D={d} P={p} C={c}"
            # 1. Bound.
            if c > d + p + TOLERANCE:
                problems.append(f"{label}: above D + P")
            if c < max(d, p) - TOLERANCE:
                problems.append(f"{label}: below max(D, P)")
            if c > values["direct"] + values["parent_plus"] + TOLERANCE:
                problems.append(f"{label}: above the total balance")
            # 2. Agreement.
            direct_level = amortized(values["direct"], values["rate"], STANDARD_MONTHS)
            parent_plus_level = amortized(
                values["parent_plus"],
                values["rate"],
                consolidation_years(values) * 12,
            )
            both_reach_minimum = (
                direct_level >= STANDARD_MINIMUM
                and parent_plus_level >= STANDARD_MINIMUM
            )
            if (both_reach_minimum or values["consolidated"]) and abs(
                c - (d + p)
            ) > TOLERANCE:
                problems.append(f"{label}: differs from D + P")
            # 5. Differential: one minimum, written here from the law.
            if not values["consolidated"]:
                total = values["direct"] + values["parent_plus"]
                reference = min(
                    max(direct_level + parent_plus_level, STANDARD_MINIMUM), total
                )
                if values["new_loan"]:
                    reference = 0
                if abs(c - reference) > TOLERANCE:
                    problems.append(f"{label}: differs from one minimum {reference}")
            # 3. One loan type.
            if values["direct"] == 0 and abs(c - p) > TOLERANCE:
                problems.append(f"{label}: no Direct Loans but C != P")
            if values["parent_plus"] == 0 and abs(c - d) > TOLERANCE:
                problems.append(f"{label}: no parent PLUS loans but C != D")
        # 4. Monotonicity, where the consolidation period holds still.
        base = get("combined_standard_repayment_payment", "base")
        for variant in ("direct_rise", "parent_plus_rise"):
            if consolidation_years(cases[variant]) != consolidation_years(
                cases["base"]
            ):
                continue
            if get("combined_standard_repayment_payment", variant) < base - TOLERANCE:
                problems.append(f"b{n} {variant}: falls as the balance rises")
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
@hypothesis.given(st.lists(borrower, min_size=1, max_size=8))
def test_one_standard_plan_minimum(borrowers):
    check(borrowers)


def test_one_standard_plan_minimum_hand_case():
    # 1,000 Direct and 20,000 parent PLUS at 6%: 11.10 + 222.04 = 233.14,
    # where the two variables each apply a minimum: 50 + 222.04.
    loans = {
        "direct": 1_000,
        "parent_plus": 20_000,
        "ffel": 0,
        "rate": 0.06,
        "consolidated": False,
        "new_loan": False,
        "direct_rise": 1,
        "parent_plus_rise": 1,
    }
    results = build([loans])
    combined = results["combined_standard_repayment_payment"][(0, "base")]
    assert combined == pytest.approx(233.14, abs=0.01)
    check([loans])
