"""Invariants for the 2018-2027 histories of state employee payroll taxes.

The tables below copy the rates and wage bases that state agencies published,
from the sources cited in each parameter file, so these tests compare the
model with those publications and not with its own parameters.

Two tests read the stored parameters without a simulation:

1. Schedule: in every month from 2015 through each table's last year, every
   parameter this history covers equals the published value for that month.
   Programs that began after 2015 read zero before their first contribution
   date: Connecticut Paid Leave (January 2021), Massachusetts PFML (October
   2019), New York Paid Family Leave (January 2018), the Oregon statewide
   transit tax (July 2018) and the Vermont Child Care Contribution (July 2024).
   New Jersey's TDI and FLI and Rhode Island's TDI predate 2018. The model does
   not encode their earlier years, so 2015-2017 read the 2018 value, an
   intended approximation that this test pins.
2. Dates: every stored value of a parameter that an annual rate averages
   begins a calendar quarter. The annual rates read only the four quarter
   starts, so this keeps them equal to the average of all twelve months.

Hypothesis draws batches of workers, each with wages, a raise, a state and an
employer headcount; a seeded population of 100 workers adds breadth. Each
batch runs as one vectorized simulation covering SIMULATED_YEARS, which
include each program's partial first year (Oregon 2018, Massachusetts 2019,
Vermont 2024). For every worker and year:

3. Differential: each contribution equals the published rate, averaged over
   all twelve months where a rate starts mid-year, times the published
   taxable wages, with New York's annual maximum.
4. Bounds: each contribution lies between zero and its highest monthly rate
   times positive wages, and wages at or below zero owe nothing.
5. Monotonicity: no contribution falls when wages rise.
6. Agreement: the employer-total path equals the worker path for
   Massachusetts and Vermont when its taxable wages equal the worker's.
7. Geography: outside its state, each contribution is zero.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

TOLERANCE = 0.01  # dollars
RATE_TOLERANCE = 1e-12
FIRST_YEAR = 2015  # policyengine_us.tools.parameters.FIRST_MODELED_YEAR
MONTHS = range(1, 13)

# Connecticut Paid Leave: 0.5% of wages up to the Social Security wage base
# from January 1, 2021 (CGS 31-49g(b)(1)).
CT_RATE, CT_START = 0.005, (2021, 1)

# Massachusetts PFML, Department of Family and Medical Leave: the family and
# medical leave rates from each month. Contributions began October 1, 2019.
# The employer may withhold all of the family rate and 40% of the medical rate;
# an employer with 25 or more covered individuals pays the other 60%.
MA_SCHEDULE = (
    ((2019, 10), 0.0013, 0.0062),
    ((2022, 1), 0.0012, 0.0056),
    ((2023, 1), 0.0011, 0.0052),
    ((2024, 1), 0.0018, 0.0070),
)
MA_MEDICAL_EMPLOYEE_SHARE = 0.4
MA_EMPLOYER_THRESHOLD = 25
MA_LAST_YEAR = 2026

# New Jersey Department of Labor and Workforce Development, employer rate
# information: worker TDI rate, worker FLI rate, TDI and FLI worker wage base.
NJ_WORKER = {
    2018: (0.0019, 0.0009, 33_700),
    2019: (0.0017, 0.0008, 34_400),
    2020: (0.0026, 0.0016, 134_900),
    2021: (0.0047, 0.0028, 138_200),
    2022: (0.0014, 0.0014, 151_900),
    2023: (0, 0.0006, 156_800),
    2024: (0, 0.0009, 161_400),
    2025: (0.0023, 0.0033, 165_400),
    2026: (0.0019, 0.0023, 171_100),
    2027: (0.0024, 0.0024, 177_100),
}

# New York Paid Family Leave, Department of Financial Services rate decisions:
# employee rate and annual maximum contribution. Contributions began in 2018.
NY_PFL = {
    2018: (0.00126, 85.56),
    2019: (0.00153, 107.97),
    2020: (0.0027, 196.72),
    2021: (0.00511, 385.34),
    2022: (0.00511, 423.71),
    2023: (0.00455, 399.43),
    2024: (0.00373, 333.25),
    2025: (0.00388, 354.53),
    2026: (0.00432, 411.91),
    2027: (0.00452, 451.81),
}

# Oregon statewide transit tax: 0.1% of wages from July 1, 2018 (ORS 320.550;
# Oregon Department of Revenue).
OR_TRANSIT_RATE, OR_TRANSIT_START = 0.001, (2018, 7)

# Rhode Island TDI, Division of Taxation advisories and Department of Labor and
# Training quick references: employee rate and taxable wage base.
RI_TDI = {
    2018: (0.011, 69_300),
    2019: (0.011, 71_000),
    2020: (0.013, 72_300),
    2021: (0.013, 74_000),
    2022: (0.011, 81_500),
    2023: (0.011, 84_000),
    2024: (0.012, 87_000),
    2025: (0.013, 89_200),
    2026: (0.011, 100_000),
}

# Vermont Child Care Contribution, Department of Taxes: 0.44% of wages from
# July 1, 2024, of which the employer may withhold 0.11% from the employee.
VT_EMPLOYEE_RATE, VT_EMPLOYER_RATE, VT_START = 0.0011, 0.0033, (2024, 7)

LAST_YEAR = 2026  # last year of the CT, OR and VT checks

# Social Security contribution and benefit base, Social Security Administration.
SS_WAGE_BASE = {2018: 128_400, 2019: 132_900, 2024: 168_600}

SIMULATED_YEARS = (2018, 2019, 2024)
STATES = ["CT", "MA", "NJ", "NY", "OR", "RI", "VT", "NH"]

P = system.parameters.gov.states


def _ma_rates(year_month):
    family = medical = 0
    for start, family_rate, medical_rate in MA_SCHEDULE:
        if year_month >= start:
            family, medical = family_rate, medical_rate
    return family, medical


def _from(start, year_month, rate):
    return rate if year_month >= start else 0


def _carried_back(table, year):
    # Years before 2018 are not encoded; the model carries 2018 back to 2015.
    return table[max(year, 2018)]


def _monthly(year, rate_in_month):
    return [rate_in_month((year, month)) for month in MONTHS]


def _published_monthly_rates(year):
    """Rates in force in each month of the year, by contribution variable."""
    ma = [_ma_rates((year, month)) for month in MONTHS]
    tdi, fli, _ = NJ_WORKER[year]
    ny_rate, _ = NY_PFL.get(year, (0, 0))
    ri_rate, _ = RI_TDI[year]
    return {
        "ct_employee_paid_leave_contribution": _monthly(
            year, lambda ym: _from(CT_START, ym, CT_RATE)
        ),
        "ma_employee_paid_leave_contribution": [
            family + MA_MEDICAL_EMPLOYEE_SHARE * medical for family, medical in ma
        ],
        "ma_employer_paid_leave_contribution": [
            (1 - MA_MEDICAL_EMPLOYEE_SHARE) * medical for _, medical in ma
        ],
        "nj_employee_temporary_disability_insurance_contribution": [tdi] * 12,
        "nj_employee_family_leave_insurance_contribution": [fli] * 12,
        "ny_employee_paid_family_leave_contribution": [ny_rate] * 12,
        "or_employee_statewide_transit_tax": _monthly(
            year, lambda ym: _from(OR_TRANSIT_START, ym, OR_TRANSIT_RATE)
        ),
        "ri_employee_temporary_disability_insurance_contribution": [ri_rate] * 12,
        "vt_employee_child_care_contribution": _monthly(
            year, lambda ym: _from(VT_START, ym, VT_EMPLOYEE_RATE)
        ),
        "vt_employer_child_care_contribution": _monthly(
            year, lambda ym: _from(VT_START, ym, VT_EMPLOYER_RATE)
        ),
    }


STATE_OF = {
    "ct_employee_paid_leave_contribution": "CT",
    "ma_employee_paid_leave_contribution": "MA",
    "ma_employer_paid_leave_contribution": "MA",
    "nj_employee_temporary_disability_insurance_contribution": "NJ",
    "nj_employee_family_leave_insurance_contribution": "NJ",
    "ny_employee_paid_family_leave_contribution": "NY",
    "or_employee_statewide_transit_tax": "OR",
    "ri_employee_temporary_disability_insurance_contribution": "RI",
    "vt_employee_child_care_contribution": "VT",
    "vt_employer_child_care_contribution": "VT",
}


def _expected(variable, year, wages, headcount):
    """Published rate times published taxable wages, for workers in the state."""
    positive = np.maximum(wages, 0)
    rate = np.mean(_published_monthly_rates(year)[variable])
    if variable.startswith(("ct_", "ma_")):
        taxable = np.minimum(positive, SS_WAGE_BASE[year])
    elif variable.startswith("nj_"):
        taxable = np.minimum(positive, NJ_WORKER[year][2])
    elif variable.startswith("ri_"):
        taxable = np.minimum(positive, RI_TDI[year][1])
    else:
        taxable = positive
    amount = rate * taxable
    if variable == "ma_employer_paid_leave_contribution":
        amount = np.where(headcount >= MA_EMPLOYER_THRESHOLD, amount, 0)
    if variable.startswith("ny_"):
        amount = np.minimum(amount, NY_PFL.get(year, (0, 0))[1])
    return amount


def _instants(last_year):
    for year in range(FIRST_YEAR, last_year + 1):
        for month in MONTHS:
            yield year, month, f"{year}-{month:02d}-01"


def test_stored_histories_match_published_tables_in_every_month():
    ma = P.ma.tax.payroll.paid_leave
    nj = P.nj.tax.payroll
    ny = P.ny.tax.payroll.paid_family_leave
    oregon = getattr(P, "or").tax.payroll.statewide_transit
    ri = P.ri.tax.payroll.temporary_disability_insurance
    vt = P.vt.tax.payroll.child_care
    for year, month, instant in _instants(LAST_YEAR):
        year_month = (year, month)
        ct_rate = _from(CT_START, year_month, CT_RATE)
        assert P.ct.tax.payroll.paid_leave.employee_rate(instant) == ct_rate
        assert oregon.employee_rate(instant) == _from(
            OR_TRANSIT_START, year_month, OR_TRANSIT_RATE
        )
        assert vt.employee_rate(instant) == _from(
            VT_START, year_month, VT_EMPLOYEE_RATE
        )
        assert vt.employer_rate(instant) == _from(
            VT_START, year_month, VT_EMPLOYER_RATE
        )
        ri_rate, ri_base = _carried_back(RI_TDI, year)
        assert ri.employee_rate(instant) == ri_rate
        assert ri.taxable_wage_base(instant) == ri_base
    for year, month, instant in _instants(MA_LAST_YEAR):
        family, medical = _ma_rates((year, month))
        assert ma.family_rate(instant) == family
        assert ma.medical_rate(instant) == medical
        if (year, month) >= MA_SCHEDULE[0][0]:
            assert ma.medical_employee_share(instant) == MA_MEDICAL_EMPLOYEE_SHARE
            assert ma.employer_headcount_threshold(instant) == MA_EMPLOYER_THRESHOLD
    for year, month, instant in _instants(2027):
        tdi, fli, base = _carried_back(NJ_WORKER, year)
        assert nj.temporary_disability_insurance.employee_rate(instant) == tdi
        assert nj.family_leave_insurance.employee_rate(instant) == fli
        assert nj.temporary_disability_insurance.taxable_wage_base(instant) == base
        ny_rate, ny_cap = NY_PFL.get(year, (0, 0))
        assert ny.employee_rate(instant) == ny_rate
        assert ny.annual_max_contribution(instant) == ny_cap


def test_quarter_averaged_parameters_change_only_at_quarter_starts():
    # A value dated inside a quarter would need the annual rate to read more
    # than the four quarter starts.
    ma = P.ma.tax.payroll.paid_leave
    averaged = [
        ma.family_rate,
        ma.medical_rate,
        ma.medical_employee_share,
        ma.employer_headcount_threshold,
        getattr(P, "or").tax.payroll.statewide_transit.employee_rate,
        P.vt.tax.payroll.child_care.employee_rate,
        P.vt.tax.payroll.child_care.employer_rate,
    ]
    for parameter in averaged:
        for entry in parameter.values_list:
            _, month, day = entry.instant_str.split("-")
            assert int(month) in (1, 4, 7, 10) and day == "01", (
                parameter.name,
                entry.instant_str,
            )


wages = st.one_of(
    st.integers(-50_000, 0).map(float),
    st.integers(0, 400_000).map(float),
)
workers = st.fixed_dictionaries(
    {
        "wages": wages,
        "raise": st.integers(0, 100_000).map(float),
        "state": st.sampled_from(STATES),
        "headcount": st.integers(0, 60),
    }
)

SEED = 20261107


def _seeded_workers(n=100):
    rng = np.random.default_rng(SEED)
    return [
        {
            "wages": float(rng.integers(-50_000, 400_001)),
            "raise": float(rng.integers(0, 100_001)),
            "state": str(rng.choice(STATES)),
            "headcount": int(rng.integers(0, 61)),
        }
        for _ in range(n)
    ]


def _people(batch):
    # Each worker appears twice, at their wages and after their raise.
    return [
        {**worker, "wages": wages, "twin": i}
        for i, worker in enumerate(batch)
        for wages in (worker["wages"], worker["wages"] + worker["raise"])
    ]


def _situation(people):
    def every_year(value):
        return {year: value for year in SIMULATED_YEARS}

    situation = {"people": {}, "households": {}}
    for i, person in enumerate(people):
        positive = max(person["wages"], 0)
        situation["people"][f"person_{i}"] = {
            "employment_income": every_year(person["wages"]),
            "employer_headcount": every_year(person["headcount"]),
            "employer_total_ma_paid_leave_taxable_wages": {
                year: min(positive, SS_WAGE_BASE[year]) for year in SIMULATED_YEARS
            },
            "employer_total_vt_child_care_contribution_wages": every_year(positive),
        }
        situation["households"][f"household_{i}"] = {
            "members": [f"person_{i}"],
            "state_code": every_year(person["state"]),
        }
    return situation


def _check(batch):
    people = _people(batch)
    wages = np.array([person["wages"] for person in people])
    headcount = np.array([person["headcount"] for person in people])
    state = np.array([person["state"] for person in people])
    positive = np.maximum(wages, 0)
    base, raised = np.arange(0, len(people), 2), np.arange(1, len(people), 2)

    sim = Simulation(situation=_situation(people))
    for year in SIMULATED_YEARS:
        monthly = _published_monthly_rates(year)
        computed = {
            variable: np.asarray(sim.calculate(variable, year), dtype=float)
            for variable in STATE_OF
        }
        for variable, amount in computed.items():
            in_state = state == STATE_OF[variable]

            # 3. Differential against the published tables.
            expected = _expected(variable, year, wages, headcount)
            np.testing.assert_allclose(
                amount[in_state],
                expected[in_state],
                atol=TOLERANCE,
                rtol=0,
                err_msg=f"{variable} {year}",
            )

            # 4. Bounds.
            top_rate = max(monthly[variable])
            assert (amount >= 0).all(), (variable, year)
            assert (amount <= top_rate * positive + TOLERANCE).all(), (variable, year)
            np.testing.assert_array_equal(amount[wages <= 0], 0)

            # 5. Monotonicity.
            assert (amount[raised] >= amount[base] - TOLERANCE).all(), (variable, year)

            # 7. Geography.
            np.testing.assert_array_equal(amount[~in_state], 0)

        # 6. Agreement of the employer-total and worker paths.
        employer_total = np.asarray(
            sim.calculate("employer_total_additional_state_payroll_tax", year),
            dtype=float,
        )
        for state_code, variable in (
            ("MA", "ma_employer_paid_leave_contribution"),
            ("VT", "vt_employer_child_care_contribution"),
        ):
            in_state = state == state_code
            np.testing.assert_allclose(
                employer_total[in_state],
                computed[variable][in_state],
                atol=TOLERANCE,
                rtol=0,
                err_msg=f"{variable} {year}",
            )


@settings(
    max_examples=4,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(workers, min_size=1, max_size=12))
def test_state_payroll_tax_history_invariants(batch):
    _check(batch)


def test_state_payroll_tax_history_invariants_seeded_population():
    _check(_seeded_workers())
