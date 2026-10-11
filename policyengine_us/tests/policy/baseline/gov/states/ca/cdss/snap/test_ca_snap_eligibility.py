"""California MCE eligibility must not acquire a net-income ceiling.

ACL 14-56 (page 6) and ACL 14-63 (page 2) deny zero-allotment households
of three or more, while one- and two-person households retain the minimum.
The YAML examples exercise real income and deductions at selected boundaries.
Hypothesis instead varies two net incomes at the same gross income, household
size and elderly/disabled status, checking the invariant across vectorized
households without supplying eligibility, categorical or member-screen outputs.
Each example has its own simulation and uses the derived California gross
limit. Whole-dollar gross and net inputs isolate this eligibility invariant
from deductions and keep every sampled net income no greater than gross.
"""

from math import floor

from hypothesis import example, given, settings, strategies as st

from policyengine_us import Simulation

YEAR = 2026
PERIOD = "2026-01"
# CDSS ACIN I-46-25, attachment I: FY2026 maximum and minimum allotments.
# https://basicneeds.ucmerced.edu/sites/g/files/ufvvjh411/f/documents/CalFreshFiles/ffy_2026_cola_acin_i-46_25.pdf
MAXIMUM_ALLOTMENTS = {
    1: 298,
    2: 546,
    3: 785,
    4: 994,
    5: 1_183,
    6: 1_421,
    7: 1_571,
    8: 1_789,
}
MINIMUM_ALLOTMENT = 24


def _situation(size, elderly, disabled):
    people, tax_units, spm_units, households = {}, {}, {}, {}
    families, marital_units = {}, {}
    for unit in range(2):
        members = []
        for member in range(size):
            name = f"u{unit}_p{member}"
            members.append(name)
            age = 65 if elderly and member == 0 else 35
            people[name] = {
                "age": {YEAR: age},
                "monthly_age": {PERIOD: age},
                "immigration_status": {YEAR: "CITIZEN"},
                "weekly_hours_worked_before_lsr": {YEAR: 40},
                "is_tax_unit_dependent": {YEAR: False},
                "is_full_time_college_student": {YEAR: False},
                "is_part_time_college_student": {YEAR: False},
                # Derive USDA disability from a qualifying status without
                # adding SSI income or categorical eligibility as an input.
                "is_permanently_disabled_veteran": {YEAR: disabled and member == 0},
            }
            # Unrelated adults buy food together but file separate returns.
            tax_units[f"t_{name}"] = {"members": [name]}
            families[f"f_{name}"] = {"members": [name]}
            marital_units[f"m_{name}"] = {"members": [name]}
        spm_units[f"s{unit}"] = {"members": members}
        households[f"h{unit}"] = {
            "members": members,
            "state_code": {YEAR: "CA"},
        }
    return {
        "people": people,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "families": families,
        "marital_units": marital_units,
        "households": households,
    }


@settings(max_examples=40, deadline=None, database=None, derandomize=True)
@given(
    size=st.integers(min_value=1, max_value=8),
    elderly=st.booleans(),
    disabled=st.booleans(),
    gross_share=st.integers(min_value=0, max_value=1_000),
    nets=st.tuples(
        st.integers(min_value=0, max_value=20_000),
        st.integers(min_value=0, max_value=20_000),
    ),
)
@example(size=1, elderly=False, disabled=False, gross_share=1_000, nets=(0, 20_000))
@example(size=2, elderly=True, disabled=False, gross_share=1_000, nets=(0, 20_000))
@example(size=3, elderly=False, disabled=True, gross_share=1_000, nets=(2_613, 2_614))
@example(size=4, elderly=True, disabled=True, gross_share=1_000, nets=(3_310, 3_311))
@example(size=5, elderly=False, disabled=False, gross_share=1_000, nets=(0, 20_000))
@example(size=6, elderly=True, disabled=False, gross_share=1_000, nets=(0, 20_000))
@example(size=7, elderly=False, disabled=True, gross_share=1_000, nets=(0, 20_000))
@example(size=8, elderly=True, disabled=True, gross_share=1_000, nets=(0, 20_000))
def test_net_income_only_changes_mce_participation_through_zero_allotment(
    size, elderly, disabled, gross_share, nets
):
    simulation = Simulation(situation=_situation(size, elderly, disabled))
    limits = simulation.calculate("tanf_non_cash_gross_income_limit", PERIOD)
    gross = [floor(float(limit) * gross_share / 1_000) for limit in limits]
    net = [min(value, income) for value, income in zip(nets, gross)]
    simulation.set_input("snap_gross_income", PERIOD, gross)
    simulation.set_input("snap_net_income", PERIOD, net)

    def calculate(variable):
        return simulation.calculate(variable, PERIOD).tolist()

    assert calculate("snap_unit_size") == [size, size]
    assert not simulation.calculate("is_snap_excluded_member", PERIOD).any()
    assert calculate("is_tanf_non_cash_hheod") == [elderly or disabled] * 2
    assert calculate("snap_gross_test_income") == gross
    assert calculate("meets_tanf_non_cash_gross_income_test") == [True, True]
    assert calculate("meets_tanf_non_cash_net_income_test") == [True, True]
    assert calculate("is_tanf_non_cash_eligible") == [True, True]
    assert calculate("meets_snap_categorical_eligibility") == [True, True]
    assert calculate("snap_max_allotment") == [MAXIMUM_ALLOTMENTS[size]] * 2

    # Independent whole-dollar benefit calculation: ceil(30% x net) uses
    # integer arithmetic, rather than the production contribution formula.
    minimum = MINIMUM_ALLOTMENT if size <= 2 else 0
    expected_allotments = [
        max(minimum, MAXIMUM_ALLOTMENTS[size] - (3 * income + 9) // 10)
        for income in net
    ]
    assert calculate("snap_allotment_before_eligibility") == expected_allotments
    assert calculate("snap_normal_allotment") == expected_allotments
    eligible = calculate("is_snap_eligible")
    assert eligible == [amount > 0 for amount in expected_allotments]
    # Holding gross and all non-income gates fixed cannot change eligibility
    # unless a three-or-more-person household crosses the zero allotment.
    if eligible[0] != eligible[1]:
        assert size >= 3
        assert (expected_allotments[0] == 0) != (expected_allotments[1] == 0)
