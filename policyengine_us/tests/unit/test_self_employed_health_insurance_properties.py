"""Properties of the self-employed health insurance deduction.

26 U.S.C. 162(l)(2)(A) limits the deduction to the taxpayer's earned income,
within the meaning of section 401(c), from the business under which the plan
is established. Section 401(c)(2)(A)(v) and (vi) determine that earned income
with regard to the section 404 plan deduction and the section 164(f) deduction
for half of self-employment tax. Form 7206 (Pub. 535 Worksheet 6-A before
2023) computes it as the plan business's net profit (line 4), less the part of
Schedule 1 line 15 attributable to that business by its share of all net
profits subject to self-employment tax (lines 5 to 8), less the Schedule 1 line
16 plan deduction (lines 9 and 10); the deduction is the smaller of the
premiums and that amount (line 14). The model treats a person's Schedule C
income as the plan business.

Hypothesis draws batches of self-employed single filers and runs each batch as
one vectorized baseline simulation. Each drawn filer appears twice, the second
time with higher premiums. For every filer and year:

1. Reference: the limit equals a closed-form Form 7206 computation that takes
   lines 15 and 16 from the model, and line 15 equals half of the
   self-employment tax.
2. Bounds: 0 <= deduction <= premiums, and deduction <= Schedule C profit less
   the attributable part of line 15 (earned income after the self-employment
   tax deduction), which never exceeds Schedule C profit.
3. Monotone in premiums: raising premiums by d raises the deduction by at
   least 0 and at most d, and leaves the limit unchanged.
4. The deduction never makes adjusted gross income negative for a filer whose
   only income is Schedule C profit: such a filer with negative AGI (from the
   plan deduction) has no health insurance deduction.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
YEARS = [2022, 2024, 2026]
PREMIUM_RAISE = 2_500


def every_year(value):
    return {year: value for year in YEARS}


def build_situation(filers):
    """One single-filer household per drawn filer, then again with higher premiums."""
    people, tax_units, households = {}, {}, {}
    for raised in (False, True):
        for i, filer in enumerate(filers):
            name = f"{'r' if raised else 'b'}{i}"
            premiums = filer["premiums"] + (PREMIUM_RAISE if raised else 0)
            people[name] = {
                "age": every_year(45),
                "is_self_employed": every_year(True),
                "self_employment_income": every_year(filer["schedule_c"]),
                "farm_operations_income": every_year(filer["farm"]),
                "partnership_self_employment_net_earnings": every_year(
                    filer["partnership"]
                ),
                "employment_income": every_year(filer["wages"]),
                "self_employed_pension_contributions_desired": every_year(
                    filer["plan"]
                ),
                "health_insurance_premiums": every_year(premiums),
            }
            tax_units[name] = {"members": [name]}
            households[name] = {"members": [name], "state_code": every_year("TX")}
    situation = {"people": people, "tax_units": tax_units, "households": households}
    return situation, len(filers)


def form_7206_limit(schedule_c, farm, partnership, line_15, line_16):
    """Form 7206 lines 4 to 10 and 13, with lines 15 and 16 as given amounts."""
    line_4 = np.maximum(schedule_c, 0)
    line_5 = line_4 + np.maximum(farm, 0) + np.maximum(partnership, 0)
    line_6 = np.where(line_5 > 0, line_4 / np.where(line_5 > 0, line_5, 1), 0)
    line_8 = line_4 - line_15 * line_6
    return np.maximum(line_8 - line_16, 0), line_8


def column(filers, key, n_copies=2):
    return np.tile(np.array([float(f[key]) for f in filers]), n_copies)


def check_properties(sim, filers, n):
    schedule_c = column(filers, "schedule_c")
    farm = column(filers, "farm")
    partnership = column(filers, "partnership")
    wages = column(filers, "wages")
    for year in YEARS:
        premiums = sim.calculate("self_employed_health_insurance_premiums", year)
        limit = sim.calculate(
            "self_employed_health_insurance_earned_income_limit", year
        )
        deduction = sim.calculate("self_employed_health_insurance_ald_person", year)
        line_15 = sim.calculate("self_employment_tax_ald_person", year)
        line_16 = sim.calculate("self_employed_pension_contribution_ald_person", year)
        se_tax = sim.calculate("self_employment_tax", year)

        # 1. Reference.
        np.testing.assert_allclose(line_15, se_tax / 2, atol=TOLERANCE)
        expected_limit, after_se_tax = form_7206_limit(
            schedule_c, farm, partnership, line_15, line_16
        )
        np.testing.assert_allclose(limit, expected_limit, atol=TOLERANCE)
        np.testing.assert_allclose(
            deduction, np.minimum(premiums, expected_limit), atol=TOLERANCE
        )

        # 2. Bounds.
        assert np.all(deduction >= 0)
        assert np.all(deduction <= premiums + TOLERANCE)
        assert np.all(deduction <= np.maximum(after_se_tax, 0) + TOLERANCE)
        assert np.all(after_se_tax <= np.maximum(schedule_c, 0) + TOLERANCE)

        # 3. Monotone and 1-Lipschitz in premiums; the limit ignores premiums.
        base, raised = deduction[:n], deduction[n:]
        assert np.all(raised >= base - TOLERANCE)
        assert np.all(raised <= base + PREMIUM_RAISE + TOLERANCE)
        np.testing.assert_allclose(limit[:n], limit[n:], atol=TOLERANCE)

        # 4. The deduction never takes Schedule C-only AGI below zero.
        schedule_c_only = (farm == 0) & (partnership == 0) & (wages == 0)
        agi = sim.calculate("adjusted_gross_income", year)
        negative_agi = schedule_c_only & (agi < -TOLERANCE)
        assert np.all(deduction[negative_agi] <= TOLERANCE)


money = st.integers(0, 120_000)
filer_strategy = st.fixed_dictionaries(
    {
        "schedule_c": st.one_of(
            st.sampled_from([-5_000, 0, 400, 434, 2_000, 160_000, 250_000]),
            st.integers(-20_000, 300_000),
        ),
        "farm": st.one_of(st.just(0), st.integers(-30_000, 100_000)),
        "partnership": st.one_of(st.just(0), st.integers(-30_000, 100_000)),
        "wages": st.one_of(st.just(0), st.integers(0, 250_000)),
        "plan": st.one_of(st.just(0), money),
        "premiums": st.one_of(st.sampled_from([0, 1_000, 6_000]), money),
    }
)
SETTINGS = dict(
    max_examples=12,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(filer_strategy, min_size=4, max_size=20))
def test_deduction_follows_form_7206(filers):
    situation, n = build_situation(filers)
    check_properties(Simulation(situation=situation), filers, n)


def test_reviewer_example_and_boundaries():
    """Fixed filers: the $2,000 example, the $400 threshold, and a wage-base case."""
    filers = [
        dict(schedule_c=2_000, farm=0, partnership=0, wages=0, plan=0, premiums=6_000),
        dict(schedule_c=434, farm=0, partnership=0, wages=0, plan=0, premiums=6_000),
        dict(schedule_c=433, farm=0, partnership=0, wages=0, plan=0, premiums=6_000),
        dict(
            schedule_c=10_000,
            farm=0,
            partnership=0,
            wages=250_000,
            plan=0,
            premiums=20_000,
        ),
        dict(
            schedule_c=30_000,
            farm=10_000,
            partnership=0,
            wages=0,
            plan=0,
            premiums=40_000,
        ),
        dict(
            schedule_c=20_000,
            farm=0,
            partnership=0,
            wages=0,
            plan=20_000,
            premiums=5_000,
        ),
    ]
    situation, n = build_situation(filers)
    sim = Simulation(situation=situation)
    check_properties(sim, filers, n)
    deduction = sim.calculate("self_employed_health_insurance_ald_person", 2022)
    # 2,000 - 2,000 x 0.9235 x 0.153 / 2.
    assert abs(deduction[0] - 1_858.7045) < TOLERANCE
    # 434 x 0.9235 = 400.80 owes self-employment tax; 433 x 0.9235 = 399.88 does not.
    assert deduction[1] < 434 - TOLERANCE
    assert abs(deduction[2] - 433) < TOLERANCE
