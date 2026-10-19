"""Invariants for the employer's deduction of state payroll premiums.

Some state programs put the premium on the employer and let it deduct up to a
share from wages without requiring it: Colorado FAMLI, Delaware Paid Leave,
Maine and Massachusetts PFML, Minnesota Paid Leave, New York PFL and DBL, the
Vermont Child Care Contribution and Washington PFML.
`employer_state_payroll_premium_deduction_share` says how much of the
permitted employee share the employer deducts (default 1); the employer pays
the rest. Hypothesis draws workers in those states, in states whose
contributions are mandatory withholding, and in a state with neither, with any
wages, employer size and share, and runs each worker three times in one
simulation: with two drawn shares and with the input left at its default. For
every worker, in 2026 and 2027:

1. The employee amount of the optional programs is the clipped share times the
   amount at the default, so the default is the full permitted share and a
   share outside 0 to 1 acts as the nearer bound.
2. The mandatory components of `employee_state_payroll_tax` do not depend on
   the share.
3. Where the employer side is modeled (CO, DE, MA, ME, VT, WA), employee plus
   employer premium does not depend on the share: the employer pays exactly
   what it does not deduct. Minnesota and New York employer costs are not
   modeled, so their employer amount is zero at any share.
4. A larger share never lowers the employee amount or raises the employer
   amount.
5. With employer-level wage totals equal to the worker's own wages (a
   one-worker employer), `employer_total_additional_state_payroll_tax` equals
   `employer_additional_state_payroll_tax`: the employer-level path and the
   per-worker path agree at any share.
6. Massachusetts' 2027 swap of the family and medical deduction caps, paired
   with DFML's swap of the two rates (Acts 2026 c. 101 ss. 25, 26, 43(a)),
   leaves each worker's employee and employer amounts where they were in
   2026, for wages under both years' wage bases.

Amounts are compared to float32 precision, within a cent.

Why Python: the YAML cases pin one share and employer size each; this checks
every program at once against drawn shares, sizes and wages, including
boundary employer sizes and shares outside 0 to 1, in one vectorized
simulation per example.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = (2026, 2027)
OPTIONAL_STATES = ("CO", "DE", "MA", "ME", "MN", "NY", "VT", "WA")
MANDATORY_STATES = ("CA", "CT", "NJ", "OR", "PA", "RI")
EMPLOYER_MODELED_STATES = ("CO", "DE", "MA", "ME", "VT", "WA")
OPTIONAL_EMPLOYEE_VARIABLES = (
    "co_employee_famli_contribution",
    "de_employee_paid_leave_contribution",
    "ma_employee_paid_leave_contribution",
    "me_employee_paid_leave_contribution",
    "mn_employee_paid_leave_contribution",
    "ny_employee_paid_family_leave_contribution",
    "ny_employee_disability_benefits_contribution",
    "vt_employee_child_care_contribution",
    "wa_employee_paid_leave_contribution",
)
# Below the 2026 Social Security wage base, so every program's wage base is
# the worker's wages in both years.
UNCAPPED_WAGES = 184_500
COPIES = 3  # drawn share a, drawn share b, input left at its default
# The model computes in float32: compare to that precision, never past a cent.
CENT = 0.01
TOLERANCE = dict(rtol=1e-6, atol=CENT)

share = st.one_of(
    st.sampled_from([0.0, 0.25, 0.5, 1.0, -0.5, 1.5]),
    st.floats(-0.5, 1.5, allow_nan=False),
)
workers = st.tuples(
    st.sampled_from(OPTIONAL_STATES + MANDATORY_STATES + ("TX",)),
    st.integers(0, 300_000),  # employment_income
    st.sampled_from([1, 9, 10, 14, 15, 20, 24, 25, 49, 50, 100]),
    share,
    share,
)


def simulate(rows):
    people, households = {}, {}
    groups = {"tax_units": {}, "spm_units": {}, "families": {}, "marital_units": {}}
    index = 0
    for state, wages, headcount, share_a, share_b in rows:
        for share_value in (share_a, share_b, None):
            person = f"person_{index}"
            people[person] = {
                "age": {year: 30 for year in YEARS},
                "employment_income": {year: wages for year in YEARS},
                "employer_headcount": {year: headcount for year in YEARS},
                "employer_total_taxable_earnings_for_social_security": {
                    year: wages for year in YEARS
                },
                "employer_total_payroll_tax_gross_wages": {
                    year: wages for year in YEARS
                },
            }
            if share_value is not None:
                people[person]["employer_state_payroll_premium_deduction_share"] = {
                    year: share_value for year in YEARS
                }
            households[f"household_{index}"] = {
                "members": [person],
                "state_code": {year: state for year in YEARS},
            }
            for name in groups:
                groups[name][f"{name}_{index}"] = {"members": [person]}
            index += 1
    return Simulation(situation={"people": people, "households": households, **groups})


def by_copy(simulation, variable, year):
    return np.asarray(simulation.calculate(variable, year)).reshape(-1, COPIES)


@settings(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(workers, min_size=4, max_size=30).map(
        # One worker in each optional state at a share strictly between 0 and
        # 1, so every program's properties compare positive amounts.
        lambda rows: (
            [(state, 60_000, 100, 0.5, 0.0) for state in OPTIONAL_STATES] + rows
        )
    )
)
def test_state_payroll_premium_deduction_share_invariants(rows):
    simulation = simulate(rows)
    states = np.array([row[0] for row in rows])
    wages = np.array([row[1] for row in rows])
    shares = np.clip(np.array([[row[3], row[4], 1.0] for row in rows]), 0, 1)
    modeled = np.isin(states, EMPLOYER_MODELED_STATES)
    unmodeled = np.isin(states, ("MN", "NY"))
    uncapped = wages <= UNCAPPED_WAGES
    optional_by_year = {}
    employer_by_year = {}
    for year in YEARS:
        optional = sum(
            by_copy(simulation, variable, year)
            for variable in OPTIONAL_EMPLOYEE_VARIABLES
        )
        total = by_copy(simulation, "employee_state_payroll_tax", year)
        employer = by_copy(simulation, "employer_additional_state_payroll_tax", year)
        employer_total = by_copy(
            simulation, "employer_total_additional_state_payroll_tax", year
        )
        default = optional[:, [2]]
        assert (default > 0).any(), "no worker with a positive optional premium"
        # Property 1.
        np.testing.assert_allclose(optional, shares * default, **TOLERANCE)
        # Property 2.
        mandatory = total - optional
        np.testing.assert_allclose(
            mandatory, mandatory[:, [2]] * np.ones((1, COPIES)), **TOLERANCE
        )
        # Property 3.
        remitted = optional + employer
        np.testing.assert_allclose(
            remitted[modeled],
            remitted[modeled][:, [2]] * np.ones((1, COPIES)),
            **TOLERANCE,
        )
        assert (employer[unmodeled] == 0).all()
        # Property 4.
        for low, high in ((0, 1), (1, 0)):
            lower = shares[:, low] <= shares[:, high]
            assert (optional[lower, low] <= optional[lower, high] + CENT).all()
            assert (employer[lower, low] >= employer[lower, high] - CENT).all()
        # Property 5.
        same_path = modeled & uncapped
        np.testing.assert_allclose(
            employer_total[same_path], employer[same_path], **TOLERANCE
        )
        optional_by_year[year] = optional
        employer_by_year[year] = employer
    # Property 6.
    ma = (states == "MA") & uncapped
    assert ma.any()
    np.testing.assert_allclose(
        optional_by_year[2027][ma], optional_by_year[2026][ma], **TOLERANCE
    )
    np.testing.assert_allclose(
        employer_by_year[2027][ma], employer_by_year[2026][ma], **TOLERANCE
    )
