"""Properties of the self-employed health insurance deduction.

26 U.S.C. 162(l)(2)(A) limits the deduction to the taxpayer's earned income,
within the meaning of section 401(c), from the business under which the plan
is established. Section 401(c)(2)(A)(v) and (vi) determine that earned income
with regard to the section 404 plan deduction and the section 164(f) deduction
for half of self-employment tax, and section 162(l)(5) makes an S corporation
shareholder's wages from the corporation their earned income. Form 7206 (Pub.
535 Worksheet 6-A before 2023), one form per plan, computes it as the plan
business's net profit (line 4), less the part of Schedule 1 line 15
attributable to that business by its share of all net profits subject to
self-employment tax (lines 5 to 8), less the Schedule 1 line 16 plan deduction
attributable to it (lines 9 and 10), or as the S corporation wages (line 11);
the deduction is the smaller of the premiums and that amount (line 14). The
plan business may be a Schedule C business, a Schedule F farm, a partnership
(K-1 box 14 code A) or an S corporation. When
self_employed_health_insurance_plan_business is not supplied, the model uses
the business with the largest earned income. The Schedule 1 line 16 plan
deduction is attributable to the businesses under which the retirement plan is
established (self_employed_pension_plan_business: by default every profitable
business, or one named business), in proportion to each one's line 8 amount,
whose sum is the retirement plan's earned income (Pub. 560 Deduction Worksheet
step 3).

Hypothesis draws batches of self-employed single filers, each with a
retirement plan business, and runs each batch as one vectorized baseline
simulation. Each drawn filer appears six times: with no named health plan
business, again with higher premiums, and once naming each of the four
businesses. For every filer and year:

1. Reference: each limit equals a closed-form Form 7206 computation for its
   plan business that takes lines 15 and 16 from the model, and line 15
   equals half of the self-employment tax. Without a named business, the
   limit is the largest of the four. The retirement plan's earned income
   equals the sum of its businesses' line 8 amounts, and line 9 across the
   businesses adds up to line 16.
2. Differential: the limit without a named business equals the largest of the
   limits the model computes when each business is named.
3. Bounds: 0 <= deduction <= premiums; the limit is at least the Schedule C
   limit (widening the base never lowers the deduction) and at most the sum
   of the four businesses' limits (one plan cannot pool businesses).
4. Monotone in premiums: raising premiums by d raises the deduction by at
   least 0 and at most d, and leaves the limit unchanged.
5. For a filer with no business losses whose income is wages and
   self-employment income, adjusted gross income is never negative: line 16
   never exceeds the retirement plan's earned income, and the health plan's
   business subtracts its share of it.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
# Model outputs are float32, whose spacing exceeds a cent above $131,072.
RTOL = 1e-6
YEARS = [2022, 2024, 2026]
PREMIUM_RAISE = 2_500
BUSINESSES = ["SCHEDULE_C", "SCHEDULE_F", "PARTNERSHIP", "S_CORPORATION"]
# (name prefix, named plan business, premium raise) for each copy of a filer.
# Businesses under which the retirement plan may be established.
PLAN_BUSINESSES = ["ALL", "SCHEDULE_C", "SCHEDULE_F", "PARTNERSHIP"]
COPIES = [("u", "UNSPECIFIED", 0), ("r", "UNSPECIFIED", PREMIUM_RAISE)] + [
    (business.lower(), business, 0) for business in BUSINESSES
]


def every_year(value):
    return {year: value for year in YEARS}


def build_situation(filers):
    """One single-filer household for each copy of each drawn filer."""
    people, tax_units, households = {}, {}, {}
    for prefix, plan_business, raise_ in COPIES:
        for i, filer in enumerate(filers):
            name = f"{prefix}{i}"
            people[name] = {
                "age": every_year(45),
                "is_self_employed": every_year(True),
                "self_employment_income": every_year(filer["schedule_c"]),
                "farm_operations_income": every_year(filer["farm"]),
                "partnership_self_employment_net_earnings": every_year(
                    filer["partnership"]
                ),
                # The partnership's earnings also enter gross income.
                "partnership_income": every_year(filer["partnership"]),
                # S corporation wages are part of employment income.
                "employment_income": every_year(filer["wages"] + filer["s_corp"]),
                "s_corp_shareholder_medicare_wages": every_year(filer["s_corp"]),
                "self_employed_pension_contributions_desired": every_year(
                    filer["plan"]
                ),
                "self_employed_pension_plan_business": every_year(
                    filer["plan_business"]
                ),
                "health_insurance_premiums": every_year(filer["premiums"] + raise_),
                "self_employed_health_insurance_plan_business": every_year(
                    plan_business
                ),
            }
            tax_units[name] = {"members": [name]}
            households[name] = {"members": [name], "state_code": every_year("TX")}
    situation = {"people": people, "tax_units": tax_units, "households": households}
    return situation, len(filers)


def form_7206_limits(
    schedule_c, farm, partnership, s_corp, plan_business, line_15, line_16
):
    """Form 7206 line 13 for each plan business, with lines 15 and 16 given.

    Also returns line 9 for each self-employment business and the retirement
    plan's earned income (Pub. 560 step 3), the sum of line 8 over the
    businesses under which the retirement plan is established.
    """
    line_4 = {
        "SCHEDULE_C": np.maximum(schedule_c, 0),
        "SCHEDULE_F": np.maximum(farm, 0),
        "PARTNERSHIP": np.maximum(partnership, 0),
    }
    line_5 = sum(line_4.values())
    safe_line_5 = np.where(line_5 > 0, line_5, 1)
    line_8 = {
        business: profit - line_15 * np.where(line_5 > 0, profit / safe_line_5, 0)
        for business, profit in line_4.items()
    }
    in_plan = {
        business: (plan_business == "ALL") | (plan_business == business)
        for business in line_4
    }
    plan_earned_income = sum(line_8[b] * in_plan[b] for b in line_4)
    safe_plan_earned_income = np.where(plan_earned_income > 0, plan_earned_income, 1)
    line_9 = {
        business: np.where(
            in_plan[business] & (plan_earned_income > 0),
            line_16 * line_8[business] / safe_plan_earned_income,
            0,
        )
        for business in line_4
    }
    line_13 = {b: np.maximum(line_8[b] - line_9[b], 0) for b in line_4}
    line_13["S_CORPORATION"] = np.maximum(s_corp, 0)
    return line_13, line_9, plan_earned_income


def close(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=TOLERANCE)


def at_least(actual, bound):
    return np.all(actual >= bound - TOLERANCE - RTOL * np.abs(bound))


def column(filers, key):
    return np.array([float(f[key]) for f in filers])


def check_properties(sim, filers, n):
    def copy(array, prefix):
        index = [p for p, _, _ in COPIES].index(prefix)
        return array[index * n : (index + 1) * n]

    schedule_c = column(filers, "schedule_c")
    farm = column(filers, "farm")
    partnership = column(filers, "partnership")
    s_corp = column(filers, "s_corp")
    plan_business = np.array([f["plan_business"] for f in filers])
    for year in YEARS:
        premiums = sim.calculate("self_employed_health_insurance_premiums", year)
        limit = sim.calculate(
            "self_employed_health_insurance_earned_income_limit", year
        )
        deduction = sim.calculate("self_employed_health_insurance_ald_person", year)
        line_15 = sim.calculate("self_employment_tax_ald_person", year)
        line_16 = sim.calculate("self_employed_pension_contribution_ald_person", year)
        se_tax = sim.calculate("self_employment_tax", year)
        agi = sim.calculate("adjusted_gross_income", year)
        plan_earned_income = sim.calculate("self_employed_pension_earned_income", year)

        # Lines 15 and 16 and the deduction for every copy.
        close(line_15, se_tax / 2)
        close(deduction, np.minimum(premiums, limit))
        # Lines 15 and 16 do not depend on premiums or the named business.
        for prefix, _, _ in COPIES[1:]:
            close(copy(line_15, prefix), copy(line_15, "u"))
            close(copy(line_16, prefix), copy(line_16, "u"))
        line_13, line_9, reference_plan_earned_income = form_7206_limits(
            schedule_c,
            farm,
            partnership,
            s_corp,
            plan_business,
            copy(line_15, "u"),
            copy(line_16, "u"),
        )
        largest = np.max(np.stack(list(line_13.values())), axis=0)

        # 1. Reference.
        close(copy(limit, "u"), largest)
        for business in BUSINESSES:
            close(copy(limit, business.lower()), line_13[business])
        close(copy(plan_earned_income, "u"), reference_plan_earned_income)
        close(sum(line_9.values()), copy(line_16, "u"))

        # 2. Differential: the default equals the best named business.
        named = np.stack([copy(limit, b.lower()) for b in BUSINESSES])
        close(copy(limit, "u"), named.max(axis=0))

        # 3. Bounds.
        assert np.all(deduction >= 0)
        assert at_least(premiums, deduction)
        assert at_least(copy(limit, "u"), line_13["SCHEDULE_C"])
        assert at_least(named.sum(axis=0), copy(limit, "u"))

        # 4. Monotone and 1-Lipschitz in premiums; the limit ignores premiums.
        base, raised = copy(deduction, "u"), copy(deduction, "r")
        assert at_least(raised, base)
        assert at_least(base + PREMIUM_RAISE, raised)
        close(copy(limit, "u"), copy(limit, "r"))

        # 5. Adjusted gross income floor for filers with no business losses.
        no_losses = (schedule_c >= 0) & (farm >= 0) & (partnership >= 0)
        for prefix, _, _ in COPIES:
            assert at_least(copy(agi, prefix)[no_losses], 0)


money = st.integers(0, 120_000)
filer_strategy = st.fixed_dictionaries(
    {
        "schedule_c": st.one_of(
            st.sampled_from([-5_000, 0, 400, 434, 2_000, 160_000, 250_000]),
            st.integers(-20_000, 300_000),
        ),
        "farm": st.one_of(st.just(0), st.integers(-30_000, 100_000)),
        "partnership": st.one_of(st.just(0), st.integers(-30_000, 100_000)),
        "s_corp": st.one_of(st.just(0), st.integers(0, 150_000)),
        "wages": st.one_of(st.just(0), st.integers(0, 250_000)),
        "plan": st.one_of(st.just(0), money),
        "plan_business": st.sampled_from(PLAN_BUSINESSES),
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


def filer(
    schedule_c=0,
    farm=0,
    partnership=0,
    s_corp=0,
    wages=0,
    plan=0,
    plan_business="ALL",
    premiums=0,
):
    return dict(
        schedule_c=schedule_c,
        farm=farm,
        partnership=partnership,
        s_corp=s_corp,
        wages=wages,
        plan=plan,
        plan_business=plan_business,
        premiums=premiums,
    )


def test_reviewer_example_and_boundaries():
    """Fixed filers: the $2,000 example, the $400 threshold, and the new bases."""
    filers = [
        filer(schedule_c=2_000, premiums=6_000),
        filer(schedule_c=434, premiums=6_000),
        filer(schedule_c=433, premiums=6_000),
        filer(schedule_c=10_000, wages=250_000, premiums=20_000),
        filer(schedule_c=30_000, farm=10_000, premiums=40_000),
        filer(schedule_c=20_000, plan=20_000, premiums=5_000),
        # A farm or a partnership as the only business.
        filer(farm=2_000, premiums=6_000),
        filer(partnership=2_000, premiums=6_000),
        # S corporation wages.
        filer(s_corp=5_000, premiums=6_000),
        # A plan deduction as large as the Schedule C profit, with retirement
        # plans under both businesses and then under the Schedule C business
        # alone; the health plan is under the larger farm.
        filer(schedule_c=20_000, plan=20_000, farm=50_000, premiums=100_000),
        filer(
            schedule_c=20_000,
            plan=20_000,
            plan_business="SCHEDULE_C",
            farm=50_000,
            premiums=100_000,
        ),
        # A farm's own retirement plan and a partner's.
        filer(farm=20_000, plan=3_000, premiums=100_000),
        filer(partnership=20_000, plan=3_000, premiums=100_000),
    ]
    situation, n = build_situation(filers)
    sim = Simulation(situation=situation)
    check_properties(sim, filers, n)
    deduction = sim.calculate("self_employed_health_insurance_ald_person", 2022)[:n]
    # 2,000 - 2,000 x 0.9235 x 0.153 / 2, for a Schedule C business, a farm and
    # a partnership alike.
    for i in (0, 6, 7):
        assert abs(deduction[i] - 1_858.7045) < TOLERANCE
    # 434 x 0.9235 = 400.80 owes self-employment tax; 433 x 0.9235 = 399.88 does not.
    assert deduction[1] < 434 - TOLERANCE
    assert abs(deduction[2] - 433) < TOLERANCE
    # Line 11: the S corporation wages, with no self-employment tax.
    assert abs(deduction[8] - 5_000) < TOLERANCE
    # Line 15: 70,000 x 0.9235 x 0.153 / 2. Line 8: Schedule C 18,587.045 and
    # farm 46,467.6125. With retirement plans under both businesses, the
    # 2022 limit (13,010.93 + 20,500) allows the 20,000 contribution, and the
    # farm's line 9 is 20,000 x 46,467.6125 / 65,054.6575.
    farm_line_8 = 50_000 - 50_000 * 0.9235 * 0.153 / 2
    plan_earned_income = 70_000 - 70_000 * 0.9235 * 0.153 / 2
    farm_line_9 = 20_000 * farm_line_8 / plan_earned_income
    assert abs(deduction[9] - (farm_line_8 - farm_line_9)) < TOLERANCE
    # With the retirement plan under the Schedule C business alone, line 16
    # is capped at that business's earned income and the farm subtracts none
    # of it.
    assert abs(deduction[10] - farm_line_8) < TOLERANCE
    # Line 13 for a farm or a partnership with its own retirement plan:
    # 20,000 - 1,412.955 - 3,000.
    for i in (11, 12):
        assert abs(deduction[i] - 15_587.045) < TOLERANCE
