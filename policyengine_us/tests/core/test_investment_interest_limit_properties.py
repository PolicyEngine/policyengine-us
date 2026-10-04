"""Vectorized properties of the investment interest limit, 26 U.S.C. 163(d).

Section 163(d)(1): the deduction "shall not exceed the net investment income
of the taxpayer for the taxable year." Form 4952 (2025), line 8: "Enter the
smaller of line 3 or line 6." Line 7 carries forward the excess of line 3 over
line 6. Its line 4g instructions say "don't enter more than the sum of lines
4b and 4e." Sources: https://www.law.cornell.edu/uscode/text/26/163#d and
https://www.irs.gov/pub/irs-pdf/f4952.pdf.

For 2017, line 5 includes the smaller of investment expenses on Schedule A
line 23 and Schedule A line 27 (Form 4952 (2017), line 5 instructions,
https://www.irs.gov/pub/irs-prior/f4952--2017.pdf). Section 67(a)'s 2% floor
applies to the generated miscellaneous expenses; section 67(h) disallows
miscellaneous itemized deductions after 2017. The independent calculation
uses raw inputs, without reading model outputs or parameters.

Each case builds one Simulation containing seeded random single and joint
returns, including dependents. Interest and dividends exclude dependents,
matching irs_gross_income; expenses, gains and elections retain the existing
all-member aggregation. Prior-year disallowed investment interest has no
input, so line 3 contains current-year interest only. Comparison cohorts
share one Simulation, avoiding dependence on computed-value invalidation.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

N = 400
YEARS = (2017, 2025, 2026)
ROLES = ("head", "spouse", "dependent")
PERSON_INPUTS = (
    "taxable_interest_income",
    "qualified_dividend_income",
    "non_qualified_dividend_income",
    "long_term_capital_gains",
    "short_term_capital_gains",
    "non_sch_d_capital_gains",
    "investment_income_elected_form_4952",
    "investment_interest_expense",
    "investment_expenses",
    "unreimbursed_business_employee_expenses",
    "tax_preparation_fees",
    "deductible_mortgage_interest",
)
LINES = {
    "3": "form_4952_total_investment_interest_expense",
    "4a": "form_4952_gross_investment_income",
    "4b": "form_4952_qualified_dividends",
    "4d": "form_4952_net_investment_gain",
    "4e": "form_4952_net_capital_gain",
    "4g": "form_4952_elected_investment_income",
    "4h": "form_4952_investment_income",
    "5": "form_4952_investment_expenses",
    "6": "form_4952_net_investment_income",
    "7": "form_4952_investment_interest_carryforward",
    "8": "investment_interest_expense_deduction",
}
# Like the section 68 property tests, comparisons allow float32 rounding
# against the operands' scale, including cancellation before a zero floor.
RTOL = 1e-6
ATOL = 0.01


def _draw(seed):
    rng = np.random.default_rng(seed)
    joint = rng.random(N) < 0.5
    present = np.column_stack((np.ones(N, dtype=bool), joint, np.ones(N, dtype=bool)))
    filers = present.copy()
    filers[:, 2] = False
    raw = {
        "present": present,
        "filers": filers,
        "adjusted_gross_income": np.round(rng.uniform(0, 400_000, N), 2),
    }
    for name in PERSON_INPUTS:
        if name in ("long_term_capital_gains", "short_term_capital_gains"):
            amount = rng.uniform(-60_000, 80_000, (N, len(ROLES)))
        elif name == "investment_income_elected_form_4952":
            # Include negative inputs to exercise the lower election bound,
            # and large elections to exercise the line 4b + line 4e cap.
            amount = rng.uniform(-20_000, 200_000, (N, len(ROLES)))
        else:
            amount = rng.uniform(0, 40_000, (N, len(ROLES)))
        zero = rng.random(amount.shape) < 0.35
        raw[name] = np.where(present & ~zero, np.round(amount, 2), 0)

    # Repeated boundary conditions complement the continuous random draws.
    no_income = np.arange(N) % 8 == 0
    for name in PERSON_INPUTS[:7]:
        raw[name][no_income] = 0
    no_interest = np.arange(N) % 8 == 1
    raw["investment_interest_expense"][no_interest] = 0
    no_election = np.arange(N) % 8 == 2
    raw["investment_income_elected_form_4952"][no_election] = 0
    return raw


def _simulate(year, raw):
    period = str(year)
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for i in range(len(raw["adjusted_gross_income"])):
        members, spouses = [], []
        for j, role in enumerate(ROLES):
            if not raw["present"][i, j]:
                continue
            person = f"u{i}_{role}"
            members.append(person)
            people[person] = {
                "age": {period: 12 if role == "dependent" else 45},
                "is_tax_unit_head": {period: role == "head"},
                "is_tax_unit_spouse": {period: role == "spouse"},
                "is_tax_unit_dependent": {period: role == "dependent"},
                **{name: {period: float(raw[name][i, j])} for name in PERSON_INPUTS},
            }
            if role == "dependent":
                marital_units[f"m{i}_dependent"] = {"members": [person]}
            else:
                spouses.append(person)
        marital_units[f"m{i}"] = {"members": spouses}
        tax_units[f"t{i}"] = {
            "members": members,
            "filing_status": {period: "JOINT" if raw["present"][i, 1] else "SINGLE"},
            "adjusted_gross_income": {period: float(raw["adjusted_gross_income"][i])},
        }
        households[f"h{i}"] = {"members": members}
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            "marital_units": marital_units,
        }
    )
    outputs = (*LINES.values(), "interest_deduction", "misc_deduction")
    return {name: simulation.calculate(name, period) for name in outputs}


def _restatement(year, raw):
    """Form 4952 lines 3-8, independently restated from person inputs."""
    filer = raw["filers"]
    line_3 = raw["investment_interest_expense"].sum(axis=1)
    line_4a = (
        (
            raw["taxable_interest_income"]
            + raw["qualified_dividend_income"]
            + raw["non_qualified_dividend_income"]
        )
        * filer
    ).sum(axis=1)
    line_4b = (raw["qualified_dividend_income"] * filer).sum(axis=1)
    long_term = raw["long_term_capital_gains"].sum(axis=1)
    short_term = raw["short_term_capital_gains"].sum(axis=1)
    distributions = raw["non_sch_d_capital_gains"].sum(axis=1)
    line_4d = np.maximum(0, long_term + short_term + distributions)
    line_4e = np.minimum(
        line_4d,
        np.maximum(0, long_term + distributions - np.maximum(0, -short_term)),
    )
    line_4g = np.minimum(
        np.maximum(0, raw["investment_income_elected_form_4952"].sum(axis=1)),
        line_4b + line_4e,
    )
    line_4h = line_4a - line_4b + line_4d - line_4e + line_4g
    expenses = raw["investment_expenses"].sum(axis=1)
    if year == 2017:
        schedule_a_line_24 = (
            expenses
            + raw["unreimbursed_business_employee_expenses"].sum(axis=1)
            + raw["tax_preparation_fees"].sum(axis=1)
        )
        schedule_a_line_27 = np.maximum(
            0,
            schedule_a_line_24 - 0.02 * np.maximum(0, raw["adjusted_gross_income"]),
        )
        line_5 = np.minimum(expenses, schedule_a_line_27)
    else:
        schedule_a_line_27 = np.zeros_like(expenses)
        line_5 = np.zeros_like(expenses)
    line_6 = np.maximum(0, line_4h - line_5)
    line_7 = np.maximum(0, line_3 - line_6)
    line_8 = np.minimum(line_3, line_6)
    line_values = (
        line_3,
        line_4a,
        line_4b,
        line_4d,
        line_4e,
        line_4g,
        line_4h,
        line_5,
        line_6,
        line_7,
        line_8,
    )
    expected = dict(zip(LINES.values(), line_values))
    expected["misc_deduction"] = schedule_a_line_27
    expected["interest_deduction"] = (
        raw["deductible_mortgage_interest"].sum(axis=1) + line_8
    )
    return expected


def _scale(raw):
    return raw["adjusted_gross_income"] + sum(
        np.abs(raw[name]).sum(axis=1) for name in PERSON_INPUTS
    )


def _slack(scale):
    return ATOL + RTOL * np.abs(scale)


def _close(actual, expected, scale, name):
    gap = np.abs(np.asarray(actual, dtype=float) - expected)
    worst = int(np.argmax(gap - _slack(scale)))
    assert np.all(gap <= _slack(scale)), (
        f"{name}, unit {worst}: {actual[worst]} vs {expected[worst]}"
    )


@pytest.mark.parametrize("year", YEARS)
def test_form_4952_matches_independent_restatement_and_bounds(year):
    raw = _draw(seed=year)
    actual = _simulate(year, raw)
    expected = _restatement(year, raw)
    scale = _scale(raw)
    slack = _slack(scale)
    for name, value in expected.items():
        _close(actual[name], value, scale, name)

    paid = actual[LINES["3"]]
    net_income = actual[LINES["6"]]
    carried = actual[LINES["7"]]
    allowed = actual[LINES["8"]]
    assert np.all(allowed >= 0)
    assert np.all(allowed <= net_income + slack)
    assert np.all(allowed <= paid + slack)
    assert np.all(carried >= 0)
    _close(carried + allowed, paid, scale, "line 7 + line 8 = line 3")

    assert np.all(actual[LINES["4e"]] >= 0)
    assert np.all(actual[LINES["4e"]] <= actual[LINES["4d"]] + slack)
    assert np.all(actual[LINES["4g"]] >= 0)
    assert np.all(
        actual[LINES["4g"]] <= actual[LINES["4b"]] + actual[LINES["4e"]] + slack
    )
    mortgage = raw["deductible_mortgage_interest"].sum(axis=1)
    _close(
        actual["interest_deduction"],
        mortgage + allowed,
        scale,
        "mortgage interest + line 8",
    )


@pytest.mark.parametrize("year", YEARS)
def test_investment_interest_limit_is_monotone(year):
    base = _draw(seed=year + 10)
    rng = np.random.default_rng(year + 20)
    changed_inputs = (
        "investment_income_elected_form_4952",
        "taxable_interest_income",
        "investment_interest_expense",
    )
    cohorts = [base]
    for name in changed_inputs:
        raised = {key: value.copy() for key, value in base.items()}
        # Raise the head's input; zero increments exercise equality, while
        # positive increments are independent of all original amounts.
        increment = np.round(rng.uniform(0, 60_000, N), 2)
        increment[np.arange(N) % 5 == 0] = 0
        raised[name][:, 0] += increment
        cohorts.append(raised)
    combined = {
        key: np.concatenate([cohort[key] for cohort in cohorts], axis=0) for key in base
    }
    actual = _simulate(year, combined)
    expected = _restatement(year, combined)
    scale = _scale(combined)
    # Verify the altered cohorts too, independently of the inequality checks.
    for name, value in expected.items():
        _close(actual[name], value, scale, name)

    base_allowed = actual[LINES["8"]][:N]
    base_carried = actual[LINES["7"]][:N]
    for i, name in enumerate(changed_inputs, start=1):
        cohort = slice(i * N, (i + 1) * N)
        slack = _slack(scale[cohort] + scale[:N])
        assert np.all(actual[LINES["8"]][cohort] >= base_allowed - slack), name
        if name == "investment_interest_expense":
            assert np.all(actual[LINES["7"]][cohort] >= base_carried - slack)
