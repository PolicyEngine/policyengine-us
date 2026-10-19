"""Invariants for the employer's deduction of state payroll premiums.

Some state programs put the premium on the employer and let it deduct up to a
share from wages without requiring it: Colorado FAMLI, Delaware Paid Leave,
Maine and Massachusetts PFML, Minnesota Paid Leave, New York PFL and DBL, the
Vermont Child Care Contribution and Washington PFML.
`employer_state_payroll_premium_deduction_share` says how much of the
permitted employee share the employer deducts (default 1); the employer pays
the rest. Hypothesis draws workers in those states, in states whose
contributions are mandatory withholding, and in a state with neither, with any
wages, employer size, share and (for Minnesota's small employer test) employer
average wage, and runs each worker three times in one simulation: with two
drawn shares and with the input left at its default. For every worker, in 2026
and 2027:

1. The employee amount of the optional programs is the clipped share times the
   amount at the default, so the default is the full permitted share and a
   share outside 0 to 1 acts as the nearer bound.
2. The mandatory components of `employee_state_payroll_tax` do not depend on
   the share.
3. Where the employer side is modeled (CO, DE, MA, ME, MN, VT, WA), employee
   plus employer premium does not depend on the share: the employer pays
   exactly what it does not deduct. The New York employer cost is not
   modeled, so its employer amount is zero at any share.
4. A larger share never lowers the employee amount or raises the employer
   amount.
5. With employer-level wage totals equal to the worker's own wages, capped at
   the Social Security base where the worker's are and at Minnesota's rounded
   base for Minnesota (a one-worker employer),
   `employer_total_additional_state_payroll_tax` equals
   `employer_additional_state_payroll_tax` in every modeled state: the
   employer-level path and the per-worker path agree at any share and
   employer size.
6. Massachusetts' 2027 swap of the family and medical deduction caps, paired
   with DFML's swap of the two rates (Acts 2026 c. 101 ss. 25, 26, 43(a)),
   leaves each worker's employee and employer amounts where they were in
   2026, for wages under both years' wage bases.
7. Minnesota matches the statute computed independently here: the premium is
   0.88% of taxable wages, or 0.66% for a small employer (30 or fewer
   employees and an average quarterly wage of at most $27,745.88); employee
   plus employer amounts equal it at any share; and the employer pays its
   minimum (half the premium, or 0.22% of wages for a small employer) plus
   the part of the rest it does not deduct (Minn. Stat. 268B.14, subds. 1,
   3 and 5a).

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
from policyengine_us.system import system

YEARS = (2026, 2027)
OPTIONAL_STATES = ("CO", "DE", "MA", "ME", "MN", "NY", "VT", "WA")
MANDATORY_STATES = ("CA", "CT", "NJ", "OR", "PA", "RI")
EMPLOYER_MODELED_STATES = ("CO", "DE", "MA", "ME", "MN", "VT", "WA")
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
SOCIAL_SECURITY_CAP = {
    year: system.parameters(f"{year}-01-01").gov.irs.payroll.social_security.cap
    for year in YEARS
}
# Minn. Stat. 268B.01, subd. 43: the Social Security base rounded to the
# nearest $1,000.
MN_TAXABLE_WAGE_BASE = {
    year: 1_000 * np.floor(SOCIAL_SECURITY_CAP[year] / 1_000 + 0.5) for year in YEARS
}
# Minnesota Paid Leave, from the statute and DEED, independent of the
# parameter files: 0.88% in 2026 and 2027 (subd. 7); employer minimum 50%
# (subd. 3); small employers 75% of the rate with an employer minimum of 25%
# of the full rate (subd. 5a(b)), if 30 or fewer employees and an average
# quarterly wage of at most $27,745.88 (subd. 5a(a); DEED's 2026 designation:
# 150% of the $73,989 statewide average annual wage, per quarter).
MN_RATE = 0.0088
MN_SMALL_MAX_HEADCOUNT = 30
MN_SMALL_MAX_AVERAGE_QUARTERLY_WAGE = 27_745.88
COPIES = 3  # drawn share a, drawn share b, input left at its default
# The model computes in float32: compare to that precision, never past a cent.
CENT = 0.01
TOLERANCE = dict(rtol=1e-6, atol=CENT)

share = st.one_of(
    st.sampled_from([0.0, 0.25, 0.5, 1.0, -0.5, 1.5]),
    st.floats(-0.5, 1.5, allow_nan=False),
)
# Whole cents, as DEED states wages: the model holds the input in float32,
# which can't tell sub-cent amounts around the limit apart.
average_quarterly_wage = st.one_of(
    st.sampled_from([0.0, 27_745.88, 27_745.89, 40_000.0]),
    st.integers(0, 6_000_000).map(lambda cents: cents / 100),
)
workers = st.tuples(
    st.sampled_from(OPTIONAL_STATES + MANDATORY_STATES + ("TX",)),
    st.integers(0, 300_000),  # employment_income
    st.sampled_from([1, 9, 10, 14, 15, 20, 24, 25, 30, 31, 49, 50, 100]),
    share,
    share,
    average_quarterly_wage,  # Minnesota small employer test only
)


def simulate(rows):
    people, households = {}, {}
    groups = {"tax_units": {}, "spm_units": {}, "families": {}, "marital_units": {}}
    index = 0
    for state, wages, headcount, share_a, share_b, average_wage in rows:
        for share_value in (share_a, share_b, None):
            person = f"person_{index}"
            people[person] = {
                "age": {year: 30 for year in YEARS},
                "employment_income": {year: wages for year in YEARS},
                "employer_headcount": {year: headcount for year in YEARS},
                "employer_total_taxable_earnings_for_social_security": {
                    year: min(wages, SOCIAL_SECURITY_CAP[year]) for year in YEARS
                },
                "employer_total_mn_paid_leave_taxable_wages": {
                    year: min(wages, MN_TAXABLE_WAGE_BASE[year]) for year in YEARS
                },
                "mn_paid_leave_employer_average_quarterly_wage": {
                    year: average_wage for year in YEARS
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
        # Every optional state gets a worker at a large employer below every
        # wage base, and one at a 9-employee employer (below the CO, MA, ME
        # and WA size thresholds; DE does not cover it; a Minnesota small
        # employer) above every wage base and New York's PFL maximum;
        # Delaware also gets a 12-employee employer (parental leave only).
        # Minnesota also gets employers at 30 and 31 employees and one of 10
        # employees whose average wage fails the small employer test. Shares
        # lie strictly between 0 and 1 or above 1, so each program's
        # properties compare positive amounts, small-employer rules and
        # capped amounts.
        lambda rows: (
            [(state, 60_000, 100, 0.5, 0.0, 0.0) for state in OPTIONAL_STATES]
            + [(state, 250_000, 9, 0.3, 1.2, 0.0) for state in OPTIONAL_STATES]
            + [("DE", 250_000, 12, 0.3, 1.2, 0.0)]
            + [
                ("MN", 60_000, 30, 0.5, 0.0, 27_745.88),
                ("MN", 60_000, 31, 0.5, 0.0, 0.0),
                ("MN", 60_000, 10, 0.5, 0.0, 27_745.89),
            ]
            + rows
        )
    )
)
def test_state_payroll_premium_deduction_share_invariants(rows):
    simulation = simulate(rows)
    states = np.array([row[0] for row in rows])
    wages = np.array([row[1] for row in rows])
    headcounts = np.array([row[2] for row in rows])
    shares = np.clip(np.array([[row[3], row[4], 1.0] for row in rows]), 0, 1)
    average_wages = np.array([row[5] for row in rows])
    modeled = np.isin(states, EMPLOYER_MODELED_STATES)
    unmodeled = states == "NY"
    mn = states == "MN"
    mn_small = (headcounts <= MN_SMALL_MAX_HEADCOUNT) & (
        average_wages <= MN_SMALL_MAX_AVERAGE_QUARTERLY_WAGE
    )
    assert mn_small[mn].any() and (~mn_small[mn]).any()
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
        same_path = modeled
        np.testing.assert_allclose(
            employer_total[same_path], employer[same_path], **TOLERANCE
        )
        # Property 7.
        mn_wages = np.minimum(np.maximum(wages, 0), MN_TAXABLE_WAGE_BASE[year])
        mn_premium = MN_RATE * np.where(mn_small, 0.75, 1) * mn_wages
        mn_minimum = np.where(mn_small, 0.25 * MN_RATE * mn_wages, 0.5 * mn_premium)
        mn_employee = by_copy(simulation, "mn_employee_paid_leave_contribution", year)
        mn_employer = by_copy(simulation, "mn_employer_paid_leave_contribution", year)
        np.testing.assert_allclose(
            by_copy(simulation, "mn_paid_leave_premium", year)[mn],
            mn_premium[mn][:, None] * np.ones((1, COPIES)),
            **TOLERANCE,
        )
        np.testing.assert_allclose(
            (mn_employee + mn_employer)[mn],
            mn_premium[mn][:, None] * np.ones((1, COPIES)),
            **TOLERANCE,
        )
        np.testing.assert_allclose(
            mn_employer[mn],
            (mn_minimum[:, None] + (1 - shares) * (mn_premium - mn_minimum)[:, None])[
                mn
            ],
            **TOLERANCE,
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


def test_massachusetts_2027_swaps_deduction_caps_and_rates():
    """Pins the four 2027 values: properties 1-6 hold whether they swap or not."""
    p = system.parameters.gov.states.ma.tax.payroll.paid_leave
    # 2026: 100% of the 0.18% family rate and 40% of the 0.70% medical rate.
    assert p.family_rate("2026-01-01") == 0.0018
    assert p.family_employee_share("2026-01-01") == 1
    assert p.medical_rate("2026-01-01") == 0.007
    assert p.medical_employee_share("2026-01-01") == 0.4
    # 2027 (Acts 2026 c. 101 ss. 25-26; DFML 2027 rates): 40% of the 0.70%
    # family rate and 100% of the 0.18% medical rate.
    assert p.family_rate("2027-01-01") == 0.007
    assert p.family_employee_share("2027-01-01") == 0.4
    assert p.medical_rate("2027-01-01") == 0.0018
    assert p.medical_employee_share("2027-01-01") == 1
