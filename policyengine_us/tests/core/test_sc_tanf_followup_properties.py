"""SC TANF gross-limit, school-level and current-loss invariants.

Sources: S.C. Code Regs. 114-1130(E), 114-1150(A), (B)(3), (C), and
DSS TANF Policy Manual Volume 67 sections 8.9 and 8.16 C and E.
"""

import numpy as np
from hypothesis import HealthCheck, example, given, settings, strategies as st

from policyengine_us import Simulation

YEAR = 2026
MONTH = "2026-01"


def simulation_for(groups):
    people, units, households = {}, {}, {}
    for index, (members, inputs) in enumerate(groups):
        names = []
        for j, member in enumerate(members):
            name = f"p{index}_{j}"
            names.append(name)
            people[name] = {key: {YEAR: value} for key, value in member.items()}
        units[f"u{index}"] = {"members": names, **inputs}
        households[f"h{index}"] = {
            "members": names,
            "state_code": {YEAR: "SC"},
        }
    return Simulation(
        situation={
            "people": people,
            "tax_units": {key: {"members": u["members"]} for key, u in units.items()},
            "spm_units": units,
            "households": households,
        }
    )


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(cents=st.integers(0, 410_700))
def test_gross_limit_includes_equality_and_is_monotone(cents):
    # January uses 2025 FPG: floor((15,650 + 2 * 5,500) / 12 * .5)
    # = 1,110; 1,110 * 1.85 = 2,053.50. Test the boundary in every draw.
    incomes = sorted({cents, 205_349, 205_350, 205_351})
    sim = simulation_for(
        [
            (
                [{"age": 40}],
                {
                    "sc_tanf_benefit_group_size": {MONTH: 3},
                    "sc_tanf_gross_income": {MONTH: income / 100},
                },
            )
            for income in incomes
        ]
    )
    actual = sim.calculate("sc_tanf_gross_income_eligible", MONTH)
    np.testing.assert_array_equal(actual, [income <= 205_350 for income in incomes])
    assert np.all(np.diff(actual.astype(int)) <= 0)


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@example(age=17, secondary=False, k12=True)
@example(age=18, secondary=False, k12=True)
@example(age=18, secondary=True, k12=True)
@example(age=19, secondary=True, k12=True)
@given(age=st.integers(0, 25), secondary=st.booleans(), k12=st.booleans())
def test_k12_attendance_never_extends_dependent_child_age(age, secondary, k12):
    sim = simulation_for(
        [
            (
                [
                    {"age": 45, "is_tax_unit_head": True},
                    {
                        "age": age,
                        "is_tax_unit_dependent": True,
                        "is_in_secondary_school": secondary,
                        "is_in_k12_school": school,
                    },
                ],
                {},
            )
            for school in (k12, not k12)
        ]
    )
    # 114-1130(E): turning general K-12 attendance on or off changes nothing.
    expected = age < 18 or (age == 18 and secondary)
    np.testing.assert_array_equal(
        sim.calculate("sc_tanf_dependent_child", MONTH),
        [False, expected, False, expected],
    )


@settings(max_examples=10, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@example(loss=1200, unearned=1000)
@given(loss=st.integers(0, 2_000), unearned=st.integers(0, 2_000))
def test_current_loss_offsets_other_income_before_payment_cap(loss, unearned):
    # Keep the signed IRS-method result and the manual's 50% arithmetic.
    # This interpretation adds no zero floor before section 8.16 E's sum.
    sim = simulation_for(
        [
            (
                [
                    {
                        "age": 40,
                        "is_tax_unit_head": True,
                        "alimony_income": unearned * 12,
                    },
                    {
                        "age": 38,
                        "is_tax_unit_spouse": True,
                        "self_employment_income_before_lsr": -loss * 12,
                    },
                    {"age": 10, "is_tax_unit_dependent": True},
                ],
                {},
            )
        ]
    )
    countable = sim.calculate("sc_tanf_countable_income", MONTH)[0]
    assert abs(countable - (unearned - loss / 2)) < 0.01
    benefit = sim.calculate("sc_tanf", MONTH)[0]
    assert 0 <= benefit <= 449
    assert benefit == np.floor(benefit)
