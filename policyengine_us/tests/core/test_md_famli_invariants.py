"""Invariants for Maryland Family and Medical Leave Insurance contributions.

The YAML cases under gov/states/md/tax/payroll/famli pin hand-computed values
at chosen points. A YAML case can't compare one person's output with another's,
so this file checks what must hold for every input: twins that differ in one
fact, and the worker-level and employer-level paths against each other. The
expected values come from Md. Code, Lab. & Empl. s. 8.3-601 and Maryland Labor's
0.9% rate, not from the parameters.

Hypothesis draws batches of workers, each alone in a household, across wage
levels, pre-tax amounts and employer sizes. Each batch runs as one vectorized
simulation, and each worker enters it as four twins: as drawn, with higher
wages, with a larger employer, and in Virginia, which has no such program.

1. Nothing before 2027: both shares and the state payroll tax are zero in 2026.
2. Base: taxable wages equal gross wages less cafeteria plan and dependent care
   amounts, floored at zero and capped at the Social Security wage base. 401(k)
   deferrals stay in.
3. Split and conservation: the employee pays 0.45% of the base at any employer.
   At 15 or more employees the two shares sum to 0.9% of the base. Below 15 the
   employer owes nothing.
4. Bounds: in 2027 each share runs from 0 to 0.45% of the $192,300 wage base.
5. Monotonicity: both shares rise weakly with wages. The employer share rises
   weakly with employer size, and the employee share ignores it.
6. Geography: every Maryland amount is zero outside Maryland.
7. Flow: employee_state_payroll_tax, employee_payroll_tax and
   spm_unit_payroll_tax exceed the Virginia twin's by the employee share, and
   household_net_income falls short of it by that share. The employer share
   leaves net income unchanged. A second simulation without the income tax,
   benefit and health cost overrides shows the same fall in net income.
8. Differential: for a one-worker employer, the employer-level total equals the
   worker-level employer share.
9. Parameters: the total rate never exceeds the 1.2% statutory cap, and the
   employee share stays within 0 to 1.

The batches set income taxes, credits, benefits and health costs to zero, as
the YAML integration cases do, which keeps them cheap. Only the check in point 7
without those overrides runs the whole model, on five households.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

TOLERANCE = 0.01  # dollars
# Net income is a sum of float32 amounts, which lose cents at high incomes.
NET_INCOME_TOLERANCE = 0.25  # dollars

TOTAL_RATE = 0.009
EMPLOYEE_RATE = 0.0045
EMPLOYER_RATE = 0.0045
HEADCOUNT_THRESHOLD = 15
RATE_CAP = 0.012
WAGE_BASE = {2026: 184_500, 2027: 192_300}

TAX_UNIT_OVERRIDES = [
    "income_tax_before_refundable_credits",
    "local_income_tax_before_refundable_credits",
]
HOUSEHOLD_OVERRIDES = [
    "household_state_tax_before_refundable_credits",
    "household_refundable_tax_credits",
    "household_benefits",
    "household_health_costs",
]
DRAWN_INPUTS = [
    "employment_income",
    "pre_tax_health_insurance_premiums",
    "health_savings_account_payroll_contributions",
    "dependent_care_employer_benefits",
    "traditional_401k_contributions",
    "employer_headcount",
]
PERSON_OUTPUTS = [
    "md_famli_taxable_wages",
    "md_employee_famli_contribution",
    "md_employer_famli_contribution",
    "md_employee_state_payroll_tax",
    "md_employer_additional_state_payroll_tax",
    "employer_additional_state_payroll_tax",
    "employer_total_additional_state_payroll_tax",
    "employer_total_md_famli_taxable_wages",
]
UNIT_OUTPUTS = [
    "employee_state_payroll_tax",
    "employee_payroll_tax",
    "spm_unit_payroll_tax",
    "household_net_income",
]

# Twin order within each drawn worker.
AS_DRAWN, MORE_WAGES, MORE_EMPLOYEES, IN_VIRGINIA = range(4)
N_TWINS = 4

# Wages at and around the 2026 and 2027 bases, then anything up to well above.
wages = st.one_of(
    st.sampled_from(
        [0.0, 1.0, 184_499.0, 184_500.0, 184_501.0, 192_299.0, 192_300.0, 192_301.0]
    ),
    st.integers(0, 400_000).map(float),
)
small_amount = st.one_of(st.just(0.0), st.integers(1, 12_000).map(float))
headcount = st.one_of(st.sampled_from([1, 14, 15, 16]), st.integers(1, 5_000))


@st.composite
def workers(draw):
    return {
        "employment_income": draw(wages),
        "pre_tax_health_insurance_premiums": draw(small_amount),
        "health_savings_account_payroll_contributions": draw(small_amount),
        "dependent_care_employer_benefits": draw(small_amount),
        "traditional_401k_contributions": draw(small_amount),
        "employer_headcount": draw(headcount),
        "raise": float(draw(st.integers(1, 100_000))),
        "more_employees": draw(st.integers(1, 100)),
    }


def _gross_wages(worker):
    """Independent wage base before the cap: 401(k) deferrals stay in."""
    return max(
        0.0,
        worker["employment_income"]
        - worker["pre_tax_health_insurance_premiums"]
        - worker["health_savings_account_payroll_contributions"]
        - worker["dependent_care_employer_benefits"],
    )


def _twins(worker, year):
    drawn = {
        **{name: worker[name] for name in DRAWN_INPUTS},
        # The employer-level path takes a one-worker employer's capped wages.
        "employer_total_taxable_earnings_for_social_security": min(
            _gross_wages(worker), WAGE_BASE[year]
        ),
    }
    return [
        ("MD", drawn),
        (
            "MD",
            {
                **drawn,
                "employment_income": drawn["employment_income"] + worker["raise"],
            },
        ),
        (
            "MD",
            {
                **drawn,
                "employer_headcount": drawn["employer_headcount"]
                + worker["more_employees"],
            },
        ),
        ("VA", drawn),
    ]


def _situation(rows, year, *, overrides=True):
    plurals = ["tax_units", "spm_units", "families", "marital_units", "households"]
    people, groups = {}, {plural: {} for plural in plurals}
    for i, (state, inputs) in enumerate(rows):
        name = f"person_{i}"
        people[name] = {
            "age": {year: 40},
            **{key: {year: value} for key, value in inputs.items()},
        }
        for plural in plurals:
            groups[plural][f"{plural}_{i}"] = {"members": [name]}
        groups["households"][f"households_{i}"]["state_code"] = {year: state}
        if overrides:
            for key in TAX_UNIT_OVERRIDES:
                groups["tax_units"][f"tax_units_{i}"][key] = {year: 0}
            for key in HOUSEHOLD_OVERRIDES:
                groups["households"][f"households_{i}"][key] = {year: 0}
    return {"people": people, **groups}


def _run(rows, year):
    sim = Simulation(situation=_situation(rows, year))
    return {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in PERSON_OUTPUTS + UNIT_OUTPUTS
    }


def _rows(batch, year):
    return [twin for worker in batch for twin in _twins(worker, year)]


def _at(run, name, twin):
    return run[name][twin::N_TWINS]


def _check_2027(batch):
    year = 2027
    run = _run(_rows(batch, year), year)
    cap = WAGE_BASE[year]
    gross = np.array([_gross_wages(w) for w in batch])
    base = np.minimum(gross, cap)
    size = np.array([w["employer_headcount"] for w in batch])

    taxable = _at(run, "md_famli_taxable_wages", AS_DRAWN)
    employee = _at(run, "md_employee_famli_contribution", AS_DRAWN)
    employer = _at(run, "md_employer_famli_contribution", AS_DRAWN)

    # 2. Base, with the 401(k) deferrals left in.
    np.testing.assert_allclose(taxable, base, atol=TOLERANCE)
    assert (taxable >= 0).all() and (taxable <= cap + TOLERANCE).all()

    # 3. Split and conservation.
    liable = size >= HEADCOUNT_THRESHOLD
    np.testing.assert_allclose(employee, EMPLOYEE_RATE * base, atol=TOLERANCE)
    np.testing.assert_allclose(
        employer, np.where(liable, EMPLOYER_RATE * base, 0), atol=TOLERANCE
    )
    np.testing.assert_allclose(
        (employee + employer)[liable], TOTAL_RATE * base[liable], atol=TOLERANCE
    )

    # 4. Bounds.
    most = EMPLOYEE_RATE * cap + TOLERANCE
    for name in ["md_employee_famli_contribution", "md_employer_famli_contribution"]:
        assert (run[name] >= 0).all() and (run[name] <= most).all(), name

    # 5. Monotonicity in wages and in employer size.
    for name in ["md_employee_famli_contribution", "md_employer_famli_contribution"]:
        assert (
            _at(run, name, MORE_WAGES) >= _at(run, name, AS_DRAWN) - TOLERANCE
        ).all(), name
    assert (
        _at(run, "md_employer_famli_contribution", MORE_EMPLOYEES)
        >= employer - TOLERANCE
    ).all()
    np.testing.assert_allclose(
        _at(run, "md_employee_famli_contribution", MORE_EMPLOYEES),
        employee,
        atol=TOLERANCE,
    )

    # 6. Geography.
    for name in PERSON_OUTPUTS:
        np.testing.assert_array_equal(_at(run, name, IN_VIRGINIA), 0, err_msg=name)

    # 7. Flow, against the Virginia twin with the same wages.
    for name in [
        "employee_state_payroll_tax",
        "employee_payroll_tax",
        "spm_unit_payroll_tax",
    ]:
        np.testing.assert_allclose(
            _at(run, name, AS_DRAWN) - _at(run, name, IN_VIRGINIA),
            employee,
            atol=TOLERANCE,
            err_msg=name,
        )
    np.testing.assert_allclose(
        _at(run, "household_net_income", IN_VIRGINIA)
        - _at(run, "household_net_income", AS_DRAWN),
        employee,
        atol=NET_INCOME_TOLERANCE,
    )
    # A larger employer can move the employer share, never net income.
    np.testing.assert_allclose(
        _at(run, "household_net_income", MORE_EMPLOYEES),
        _at(run, "household_net_income", AS_DRAWN),
        atol=NET_INCOME_TOLERANCE,
    )

    # 8. Worker-level and employer-level paths agree for a one-worker employer.
    np.testing.assert_allclose(
        _at(run, "employer_total_md_famli_taxable_wages", AS_DRAWN),
        base,
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        _at(run, "employer_total_additional_state_payroll_tax", AS_DRAWN),
        _at(run, "employer_additional_state_payroll_tax", AS_DRAWN),
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        _at(run, "employer_additional_state_payroll_tax", AS_DRAWN),
        employer,
        atol=TOLERANCE,
    )


def _check_2026(batch):
    year = 2026
    run = _run(_rows(batch, year), year)

    # 1. The base exists, but no contribution does.
    for name in [
        "md_employee_famli_contribution",
        "md_employer_famli_contribution",
        "md_employee_state_payroll_tax",
        "md_employer_additional_state_payroll_tax",
        "employer_additional_state_payroll_tax",
        "employer_total_additional_state_payroll_tax",
        "employee_state_payroll_tax",
    ]:
        np.testing.assert_array_equal(run[name], 0, err_msg=name)
    np.testing.assert_allclose(
        _at(run, "employee_payroll_tax", AS_DRAWN),
        _at(run, "employee_payroll_tax", IN_VIRGINIA),
        atol=TOLERANCE,
    )
    assert (run["md_famli_taxable_wages"] <= WAGE_BASE[year] + TOLERANCE).all()


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(workers(), min_size=10, max_size=40))
def test_contribution_invariants_2027(batch):
    _check_2027(batch)


@settings(**SETTINGS)
@given(st.lists(workers(), min_size=10, max_size=40))
def test_no_contribution_in_2026(batch):
    _check_2026(batch)


def test_net_income_falls_by_the_employee_share_without_overrides():
    # The batches above zero out income taxes and benefits. These households
    # run the whole model, with and without the employee share, and the only
    # difference in net income is that share.
    year = 2027
    wage_levels = [15_000.0, 50_000.0, 120_000.0, 192_300.0, 300_000.0]
    rows = [("MD", {"employment_income": level}) for level in wage_levels]
    situation = _situation(rows, year, overrides=False)
    base = Simulation(situation=situation)
    no_share = Simulation(situation=situation)
    no_share.set_input(
        "md_employee_state_payroll_tax", year, np.zeros(len(wage_levels))
    )
    share = np.minimum(wage_levels, WAGE_BASE[year]) * EMPLOYEE_RATE
    np.testing.assert_allclose(
        np.asarray(base.calculate("md_employee_state_payroll_tax", year), dtype=float),
        share,
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        np.asarray(no_share.calculate("household_net_income", year), dtype=float)
        - np.asarray(base.calculate("household_net_income", year), dtype=float),
        share,
        atol=NET_INCOME_TOLERANCE,
    )


def test_parameters_stay_within_the_statute():
    # s. 8.3-601(a)(1)(ii) caps the total rate at 1.2%, whatever the Secretary
    # sets each year.
    famli = system.parameters.gov.states.md.tax.payroll.famli
    rates = [entry.value for entry in famli.total_rate.values_list]
    shares = [entry.value for entry in famli.employee_share.values_list]
    assert rates and all(0 <= rate <= RATE_CAP for rate in rates)
    assert shares and all(0 <= share <= 1 for share in shares)
    assert famli.total_rate("2026-12-31") == 0
    assert famli.total_rate("2027-01-01") == pytest.approx(TOTAL_RATE)
    assert famli.employee_share("2027-01-01") == pytest.approx(0.5)
    assert famli.employer_headcount_threshold("2027-01-01") == HEADCOUNT_THRESHOLD
