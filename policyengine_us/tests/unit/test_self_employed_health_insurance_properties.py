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
attributable to it (lines 9 and 10), or as the S corporation wages (line 11).
The deduction is the smaller of line 3 and that amount (line 14), where line 3
adds eligible long-term care premiums (line 2) to the medical premiums (line 1).
The plan business may be a Schedule C business, a Schedule F farm, a partnership
(K-1 box 14 code A) or an S corporation. When
self_employed_health_insurance_plan_business is not supplied, the model uses
the business with the largest earned income. The model treats a person's
Schedule C income, SSTB and non-SSTB together, as one business.

The line 16 plan deduction is attributable to the businesses under which the
retirement plan is established (self_employed_pension_plan_business). With one
named business, all of it is attributable to that business. By default every
profitable business has a plan and the person chooses how much each plan
carries, so line 9 for a business is the least its plan must carry while the
other plans carry as much as they can. Each plan stays within its own
business's Pub. 560 worksheet limits, and the plans share one dollar limit and
one elective deferral limit. The reference finds that least share with an
exact linear program, solved here by enumerating the vertices of its feasible
set, so it shares no code with the model's closed form.

Hypothesis draws batches of self-employed single filers, each with a
retirement plan business, and runs each batch as one vectorized baseline
simulation. Each drawn filer appears six times: with no named health plan
business, again with higher premiums, and once naming each of the four
businesses. For every filer and year:

1. Reference: Schedule 1 line 15 equals half of the self-employment tax
   computed here from Schedule SE, and each limit equals a Form 7206
   computation for its plan business from that line 15, the model's line 16
   and line 9 from the linear program. Without a named business, the limit is
   the largest of the four. The deduction is the smaller of line 3 and that
   reference limit. Line 3 adds the drawn long-term care premiums, up to the
   limit for ages 41 to 50 (line 2), to the medical premiums (line 1).
2. Differential: the limit without a named business equals the largest of the
   limits the model computes when each business is named.
3. Bounds: 0 <= deduction <= line 3; the limit is at least the Schedule C
   limit, and each business's limit is at least its line 8 less line 16, since
   no business's plan carries more than line 16.
4. Monotone in premiums: raising the medical premiums by d raises the
   deduction by at least 0 and at most d, and leaves the limit unchanged.
5. For a filer with no business losses whose income is wages and
   self-employment income, adjusted gross income is never negative: the plans
   carry line 16 out of their own businesses' earned income, and the health
   plan's business keeps only what its plan doesn't carry.
6. Line 2 and Schedule A: the long-term care part is the smaller of line 2
   and what the deduction leaves after line 1, and Schedule A keeps line 3
   less the deduction, so each premium in line 3 counts once.

Two tests need no simulation. One checks the model's line 9 function against
the linear program over drawn earned incomes, contributions and limits,
including plan rates other than 25%. The other checks the model's single-plan
limit, which the plan limit's property tests tie to the Pub. 560 worksheet,
against the program's largest total for one plan and for two, so the
program's constraints are the worksheet's.

The model computes in float32, whose spacing passes a cent above $131,072, so
comparisons allow a relative error of 1e-6, of the amounts that enter each
result, on top of the $0.01 tolerance.
"""

import functools
import itertools

import numpy as np
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.variables.household.expense.retirement.self_employed_pension_contribution_limit import (
    plan_deduction_attributable_to_business,
    self_employed_plan_limit,
)

TOLERANCE = 0.01
# Model outputs are float32, whose spacing exceeds a cent above $131,072.
RTOL = 1e-6
YEARS = [2022, 2024, 2026]
PREMIUM_RAISE = 2_500

# Schedule SE, as test data rather than model parameters.
# 26 U.S.C. 1402(a)(12): net earnings are 92.35% of net profit.
NET_EARNINGS_SHARE = 0.9235
# 26 U.S.C. 1402(b)(2): no net earnings below $400.
NET_EARNINGS_EXEMPTION = 400
# 26 U.S.C. 1401(a) and (b).
SOCIAL_SECURITY_RATE = 0.124
MEDICARE_RATE = 0.029
# Contribution and benefit bases, https://www.ssa.gov/oact/cola/cbb.html.
WAGE_BASE = {2022: 147_000, 2024: 168_600, 2026: 184_500}
# 26 U.S.C. 213(d)(10): eligible long-term care premiums at ages 41 to 50
# (Rev. Proc. 2021-45, 2023-34 and 2025-32), as test data.
LONG_TERM_CARE_LIMIT_AGE_45 = {2022: 850, 2024: 880, 2026: 930}
# Plan contribution rate: 26 U.S.C. 404(a)(3)(A)(i)(I) and 404(h)(1)(C).
PLAN_RATE = 0.25
# Section 415(c) dollar limit and section 402(g) elective deferral limit, from
# IRS Notices 2021-61 (2022), 2023-75 (2024) and 2025-67 (2026). The filers
# are 45, so they have no catch-up room.
PLAN_LIMITS = {
    2022: dict(dollar_limit=61_000, deferral=20_500),
    2024: dict(dollar_limit=69_000, deferral=23_000),
    2026: dict(dollar_limit=72_000, deferral=24_500),
}
BUSINESSES = ["SCHEDULE_C", "SCHEDULE_F", "PARTNERSHIP", "S_CORPORATION"]
SELF_EMPLOYMENT_BUSINESSES = BUSINESSES[:3]
# Businesses under which the retirement plan may be established; ALL, the
# default, puts a plan under every profitable one.
PLAN_BUSINESSES = ["ALL", "SCHEDULE_C", "SCHEDULE_F", "PARTNERSHIP"]
# (name prefix, named health plan business, premium raise) for each copy of a
# filer.
COPIES = [("u", "UNSPECIFIED", 0), ("r", "UNSPECIFIED", PREMIUM_RAISE)] + [
    (business.lower(), business, 0) for business in BUSINESSES
]

# The linear program behind line 9. Two plans: the plans under the other
# businesses together (their limits are linear in earned income, so they act
# as one plan with the sum of their earned income), then the plan under this
# business. x = [employer contributions, regular elective deferrals, catch-up
# contributions] for the other plans, then for this one.
LP_ROWS = np.array(
    [
        # Each plan, from Pub. 560's Deduction Worksheet for Self-Employed:
        # employer contributions at most the reduced rate times earned income
        # (steps 4 and 5), at most half of earned income less deferrals (step
        # 12), and all contributions at most earned income (404(a)(8)(C)).
        [1, 0, 0, 0, 0, 0],
        [2, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 0, 0, 2, 1, 0],
        [0, 0, 0, 1, 1, 1],
        # Shared: the regular and catch-up elective deferral room (402(g) and
        # 414(v)) and the dollar limit on employer contributions and regular
        # deferrals (415(c)).
        [0, 1, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 1],
        [1, 1, 0, 1, 1, 0],
        # No negative contributions.
        *(-np.eye(6)),
    ],
    dtype=float,
)
# The program's arithmetic is float64, accurate to about 1e-10 dollars.
LP_TOLERANCE = 1e-6


def lp_bounds(this, other, rate, dollar_limit, regular_room, catch_up_room):
    """Right-hand sides of LP_ROWS for each case."""
    reduced_rate = rate / (1 + rate)
    zeros = np.zeros_like(this)
    return np.stack(
        [
            reduced_rate * other,
            other,
            other,
            reduced_rate * this,
            this,
            this,
            regular_room + zeros,
            catch_up_room + zeros,
            dollar_limit + zeros,
        ]
        + [zeros] * 6,
        axis=-1,
    )


@functools.lru_cache(maxsize=None)
def vertex_systems(with_total):
    """Inverses of every set of active constraints that fixes one point.

    With with_total, each set adds the constraint that the contributions sum
    to the plan deduction.
    """
    columns = LP_ROWS.shape[1]
    chosen, inverses = [], []
    for rows in itertools.combinations(range(len(LP_ROWS)), columns - with_total):
        system = LP_ROWS[list(rows)]
        if with_total:
            system = np.vstack([system, np.ones(columns)])
        if abs(np.linalg.det(system)) > 1e-9:
            chosen.append(rows)
            inverses.append(np.linalg.inv(system))
    return np.array(chosen), np.array(inverses)


def lp_minimum(objective, bounds, total=None):
    """Least objective over LP_ROWS x <= bounds, and sum(x) == total if given.

    The feasible set is a bounded polytope, so the minimum is at one of its
    vertices; returns infinity where the set is empty.
    """
    chosen, inverses = vertex_systems(total is not None)
    rhs = bounds[:, chosen]
    if total is not None:
        rhs = np.concatenate(
            [rhs, np.broadcast_to(total[:, None, None], rhs.shape[:2] + (1,))],
            axis=2,
        )
    points = np.einsum("sij,csj->csi", inverses, rhs)
    slack = bounds[:, None, :] - points @ LP_ROWS.T
    feasible = np.all(slack >= -LP_TOLERANCE, axis=2)
    return np.where(feasible, points @ objective, np.inf).min(axis=1)


def lp_largest_total(this, other, rate, dollar_limit, regular_room, catch_up_room):
    """Largest total contribution to the two plans."""
    bounds = lp_bounds(this, other, rate, dollar_limit, regular_room, catch_up_room)
    return -lp_minimum(-np.ones(6), bounds)


def lp_least_share(total, this, other, rate, dollar_limit, regular_room, catch_up_room):
    """Least that this business's plan carries of a total the plans share."""
    bounds = lp_bounds(this, other, rate, dollar_limit, regular_room, catch_up_room)
    return lp_minimum(np.array([0, 0, 0, 1, 1, 1.0]), bounds, total)


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
                "sstb_self_employment_income": every_year(filer["sstb"]),
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
                "long_term_health_insurance_premiums": every_year(
                    filer["long_term_care"]
                ),
                "self_employed_health_insurance_plan_business": every_year(
                    plan_business
                ),
            }
            tax_units[name] = {"members": [name]}
            households[name] = {"members": [name], "state_code": every_year("TX")}
    situation = {"people": people, "tax_units": tax_units, "households": households}
    return situation, len(filers)


def schedule_se_deduction(year, schedule_c, farm, partnership, wages):
    """Schedule 1 line 15: half of Schedule SE self-employment tax."""
    net_earnings = (schedule_c + farm + partnership) * NET_EARNINGS_SHARE
    net_earnings = np.where(net_earnings < NET_EARNINGS_EXEMPTION, 0, net_earnings)
    social_security_room = np.maximum(WAGE_BASE[year] - wages, 0)
    tax = SOCIAL_SECURITY_RATE * np.minimum(
        net_earnings, social_security_room
    ) + MEDICARE_RATE * np.maximum(net_earnings, 0)
    return tax / 2


def form_7206_limits(
    year, schedule_c, farm, partnership, s_corp, plan_business, line_15, line_16
):
    """Form 7206 line 13 for each plan business, with lines 15 and 16 given.

    Also returns line 8 and line 9 for each self-employment business.
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
    limits = PLAN_LIMITS[year]
    room = (PLAN_RATE, limits["dollar_limit"], limits["deferral"], 0)
    all_line_8 = sum(line_8.values())
    line_9 = {}
    for business in SELF_EMPLOYMENT_BUSINESSES:
        this = line_8[business]
        other = all_line_8 - this
        # Line 16 comes from the model in float32 and may pass the largest
        # total by a rounding error.
        total = np.minimum(line_16, lp_largest_total(this, other, *room))
        least = lp_least_share(total, this, other, *room)
        line_9[business] = np.select(
            [plan_business == "ALL", plan_business == business],
            [least, line_16],
            0,
        )
    line_13 = {
        business: np.maximum(line_8[business] - line_9[business], 0)
        for business in SELF_EMPLOYMENT_BUSINESSES
    }
    line_13["S_CORPORATION"] = np.maximum(s_corp, 0)
    return line_13, line_8, line_9


def close(actual, expected, scale=0):
    """Equal within $0.01 plus RTOL of the larger of the result and scale."""
    np.testing.assert_array_less(
        np.abs(actual - expected),
        TOLERANCE + RTOL * np.maximum(np.abs(expected), scale),
    )


def at_least(actual, bound, scale=0):
    return np.all(actual >= bound - TOLERANCE - RTOL * np.maximum(np.abs(bound), scale))


def column(filers, key):
    return np.array([float(f[key]) for f in filers])


def check_properties(sim, filers, n):
    def copy(array, prefix):
        index = [p for p, _, _ in COPIES].index(prefix)
        return array[index * n : (index + 1) * n]

    # The model's Schedule C is SSTB and non-SSTB income together.
    schedule_c = column(filers, "schedule_c") + column(filers, "sstb")
    farm = column(filers, "farm")
    partnership = column(filers, "partnership")
    s_corp = column(filers, "s_corp")
    # S corporation wages are Social Security wages too.
    wages = column(filers, "wages") + s_corp
    long_term_care = column(filers, "long_term_care")
    plan_business = np.array([f["plan_business"] for f in filers])
    for year in YEARS:
        premiums = sim.calculate("self_employed_health_insurance_premiums", year)
        # Line 2: the drawn premiums up to the age 41-50 limit, for every copy.
        line_2 = np.tile(
            np.minimum(long_term_care, LONG_TERM_CARE_LIMIT_AGE_45[year]),
            len(COPIES),
        )
        line_3 = premiums + line_2
        long_term_care_part = sim.calculate(
            "self_employed_health_insurance_ald_long_term_care_part", year
        )
        schedule_a = sim.calculate("itemized_medical_expenses", year)
        limit = sim.calculate(
            "self_employed_health_insurance_earned_income_limit", year
        )
        deduction = sim.calculate("self_employed_health_insurance_ald_person", year)
        line_15 = sim.calculate("self_employment_tax_ald_person", year)
        line_16 = sim.calculate("self_employed_pension_contribution_ald_person", year)
        agi = sim.calculate("adjusted_gross_income", year)

        # Line 15 from Schedule SE, and line 16, for every copy.
        expected_line_15 = schedule_se_deduction(
            year, schedule_c, farm, partnership, wages
        )
        for prefix, _, _ in COPIES:
            close(copy(line_15, prefix), expected_line_15)
        # Line 16 does not depend on premiums or the named health plan
        # business, so the plan limit never reads the health insurance
        # deduction.
        for prefix, _, _ in COPIES[1:]:
            close(copy(line_16, prefix), copy(line_16, "u"))
        plan_deduction = copy(line_16, "u").astype(float)
        line_13, line_8, line_9 = form_7206_limits(
            year,
            schedule_c,
            farm,
            partnership,
            s_corp,
            plan_business,
            expected_line_15,
            plan_deduction,
        )
        largest = np.max(np.stack(list(line_13.values())), axis=0)
        # Every amount that enters a limit, for the float32 tolerance.
        scale = (
            np.maximum(schedule_c, 0)
            + np.maximum(farm, 0)
            + np.maximum(partnership, 0)
            + s_corp
            + plan_deduction
        )
        # The reference limit for every copy, in the simulation's order.
        reference_limit = np.concatenate(
            [
                largest if business == "UNSPECIFIED" else line_13[business]
                for _, business, _ in COPIES
            ]
        )

        # 1. Reference.
        close(
            deduction,
            np.minimum(line_3, reference_limit),
            np.tile(scale, len(COPIES)),
        )
        close(copy(limit, "u"), largest, scale)
        for business in BUSINESSES:
            close(copy(limit, business.lower()), line_13[business], scale)

        # 2. Differential: the default equals the best named business.
        named = np.stack([copy(limit, b.lower()) for b in BUSINESSES])
        close(copy(limit, "u"), named.max(axis=0))

        # 3. Bounds.
        assert np.all(deduction >= 0)
        assert at_least(line_3, deduction)
        assert at_least(copy(limit, "u"), copy(limit, "schedule_c"))
        for business in SELF_EMPLOYMENT_BUSINESSES:
            assert at_least(
                copy(limit, business.lower()),
                line_8[business] - plan_deduction,
                scale,
            )

        # 4. Monotone and 1-Lipschitz in premiums; the limit ignores premiums.
        base, raised = copy(deduction, "u"), copy(deduction, "r")
        assert at_least(raised, base)
        assert at_least(base + PREMIUM_RAISE, raised)
        close(copy(limit, "u"), copy(limit, "r"))

        # 5. Adjusted gross income for filers with no business losses.
        no_losses = (
            (column(filers, "schedule_c") >= 0)
            & (column(filers, "sstb") >= 0)
            & (farm >= 0)
            & (partnership >= 0)
        )
        for prefix, _, _ in COPIES:
            assert at_least(copy(agi, prefix)[no_losses], 0, scale[no_losses])

        # 6. Line 2 takes what the deduction leaves after line 1, and
        # Schedule A keeps line 3 less the deduction.
        close(
            long_term_care_part,
            np.minimum(line_2, deduction - np.minimum(premiums, deduction)),
        )
        close(schedule_a, line_3 - deduction)


money = st.integers(0, 120_000)
# Smaller businesses, whose plans can reach their earned income.
small_business = st.sampled_from([5_000, 10_000, 20_000])
filer_strategy = st.fixed_dictionaries(
    {
        "schedule_c": st.one_of(
            st.sampled_from([-5_000, 0, 400, 434, 2_000, 160_000, 250_000]),
            st.integers(-20_000, 300_000),
        ),
        "sstb": st.one_of(st.just(0), st.integers(-20_000, 100_000)),
        "farm": st.one_of(st.just(0), small_business, st.integers(-30_000, 100_000)),
        "partnership": st.one_of(
            st.just(0), small_business, st.integers(-30_000, 100_000)
        ),
        "s_corp": st.one_of(st.just(0), st.integers(0, 150_000)),
        "wages": st.one_of(st.just(0), st.integers(0, 250_000)),
        "plan": st.one_of(st.just(0), money),
        # ALL, the default, twice as often as each named business.
        "plan_business": st.sampled_from(["ALL"] + PLAN_BUSINESSES),
        "premiums": st.one_of(st.sampled_from([0, 1_000, 6_000]), money),
        "long_term_care": st.one_of(st.just(0), st.integers(1, 2_000)),
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
    sstb=0,
    farm=0,
    partnership=0,
    s_corp=0,
    wages=0,
    plan=0,
    plan_business="ALL",
    premiums=0,
    long_term_care=0,
):
    return dict(
        schedule_c=schedule_c,
        sstb=sstb,
        farm=farm,
        partnership=partnership,
        s_corp=s_corp,
        wages=wages,
        plan=plan,
        plan_business=plan_business,
        premiums=premiums,
        long_term_care=long_term_care,
    )


def test_reviewer_example_and_boundaries():
    """Fixed filers: the $2,000 example, the $400 threshold, the new bases,
    long-term care premiums and line 9 with plans under two businesses."""
    filers = [
        filer(schedule_c=2_000, premiums=6_000),
        filer(schedule_c=434, premiums=6_000),
        filer(schedule_c=433, premiums=6_000),
        filer(schedule_c=10_000, wages=250_000, premiums=20_000),
        filer(schedule_c=30_000, farm=10_000, premiums=40_000),
        filer(schedule_c=20_000, plan=20_000, premiums=5_000),
        # SSTB and non-SSTB Schedule C income netted as one business.
        filer(schedule_c=30_000, sstb=-10_000, premiums=30_000),
        # A farm or a partnership as the only business.
        filer(farm=2_000, premiums=6_000),
        filer(partnership=2_000, premiums=6_000),
        # S corporation wages.
        filer(s_corp=5_000, premiums=6_000),
        # A retirement plan under the Schedule C business only, with a plan
        # deduction as large as its earned income: the farm keeps its own.
        filer(
            schedule_c=20_000,
            plan=20_000,
            plan_business="SCHEDULE_C",
            farm=50_000,
            premiums=100_000,
        ),
        # Long-term care premiums under an S corporation plan: in 2022, line 3
        # is 6,000 + min(2,000, 850) = 6,850, above line 11.
        filer(s_corp=6_500, premiums=6_000, long_term_care=2_000),
        # Plans under two businesses, as in the YAML tests' Cases 26 and 27.
        filer(schedule_c=50_000, partnership=10_000, plan=40_000, premiums=100_000),
        filer(schedule_c=43_000, partnership=43_000, plan=60_000, premiums=100_000),
    ]
    situation, n = build_situation(filers)
    sim = Simulation(situation=situation)
    check_properties(sim, filers, n)
    deduction = sim.calculate("self_employed_health_insurance_ald_person", 2022)[:n]
    # 2,000 - 2,000 x 0.9235 x 0.153 / 2, for a Schedule C business, a farm and
    # a partnership alike.
    for i in (0, 7, 8):
        assert abs(deduction[i] - 1_858.7045) < TOLERANCE
    # 434 x 0.9235 = 400.80 owes self-employment tax; 433 x 0.9235 = 399.88 does not.
    assert deduction[1] < 434 - TOLERANCE
    assert abs(deduction[2] - 433) < TOLERANCE
    # A plan deduction equal to net profit leaves no limit.
    assert deduction[5] <= TOLERANCE
    # 20,000 of netted Schedule C profit: 20,000 - 20,000 x 0.9235 x 0.153 / 2.
    assert abs(deduction[6] - 18_587.045) < TOLERANCE
    # Line 11: the S corporation wages, with no self-employment tax.
    assert abs(deduction[9] - 5_000) < TOLERANCE
    # Farm line 13: 50,000 - 50,000 / 70,000 x (70,000 x 0.9235 x 0.153 / 2).
    assert abs(deduction[10] - (50_000 - 50_000 * 0.9235 * 0.153 / 2)) < TOLERANCE
    # Line 11, 6,500, exceeds the 6,000 of medical premiums.
    assert abs(deduction[11] - 6_500) < TOLERANCE
    # In 2026 the Schedule C plan carries 28,217.409 of 35,652.227 and the
    # Schedule C business keeps 18,250.2035; with two equal businesses, each
    # plan carries 8,515.1413 of 40,484.8587.
    deduction = sim.calculate("self_employed_health_insurance_ald_person", 2026)[:n]
    assert abs(deduction[12] - 18_250.2035) < 0.02
    assert abs(deduction[13] - 31_447.0055) < 0.02


# Draws for the line 9 function: earned income of the business and of the
# other plans, the shared limits and room, and the plan deduction as a share
# of the largest total.
earned_income = st.one_of(
    st.just(0.0),
    st.floats(0, 40_000),
    st.floats(0, 400_000),
)
plan_case = st.fixed_dictionaries(
    {
        "this": earned_income,
        "other": earned_income,
        "rate": st.sampled_from([0.25, 0.25, 0.15, 0.4, 1.0]),
        "dollar_limit": st.one_of(
            st.sampled_from([61_000.0, 69_000.0, 72_000.0]), st.floats(10_000, 72_000)
        ),
        "regular_room": st.one_of(
            st.sampled_from([0.0, 20_500.0, 24_500.0]), st.floats(0, 24_500)
        ),
        "catch_up_room": st.one_of(
            st.sampled_from([0.0, 7_500.0, 11_250.0]), st.floats(0, 11_250)
        ),
        "share": st.one_of(st.just(1.0), st.floats(0, 1), st.floats(0.9, 1)),
    }
)


def plan_arrays(cases):
    return {key: np.array([c[key] for c in cases]) for key in cases[0]}


@settings(
    max_examples=60,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(st.lists(plan_case, min_size=1, max_size=40))
@example(
    # Case 26: the partnership's plan, at its earned income, frees deferral
    # room at 50 cents on the dollar.
    [
        dict(
            this=46_467.6125,
            other=9_293.5225,
            rate=0.25,
            dollar_limit=72_000.0,
            regular_room=24_500.0,
            catch_up_room=0.0,
            share=1.0,
        ),
        # Case 27: the other plan, below its earned income, does the same.
        dict(
            this=39_962.14675,
            other=39_962.14675,
            rate=0.25,
            dollar_limit=72_000.0,
            regular_room=24_500.0,
            catch_up_room=0.0,
            share=1.0,
        ),
        # A catch-up contribution ends at the kink between the two faces.
        dict(
            this=46_467.6125,
            other=9_293.5225,
            rate=0.25,
            dollar_limit=72_000.0,
            regular_room=24_500.0,
            catch_up_room=8_000.0,
            share=1.0,
        ),
    ]
)
def test_line_9_is_the_least_share_the_plans_allow(cases):
    c = plan_arrays(cases)
    room = (c["rate"], c["dollar_limit"], c["regular_room"], c["catch_up_room"])
    largest = lp_largest_total(c["this"], c["other"], *room)
    total = c["share"] * largest
    least = lp_least_share(total, c["this"], c["other"], *room)
    model = plan_deduction_attributable_to_business(total, c["this"], c["other"], *room)
    np.testing.assert_allclose(model, least, rtol=1e-9, atol=1e-6)


@settings(
    max_examples=40,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(st.lists(plan_case, min_size=1, max_size=40))
def test_plan_limit_is_the_programs_largest_total(cases):
    """The linear program's constraints reproduce the worksheet's limit, for
    one plan and for plans under two businesses together."""
    c = plan_arrays(cases)
    room = (c["rate"], c["dollar_limit"], c["regular_room"], c["catch_up_room"])
    zeros = np.zeros_like(c["this"])
    np.testing.assert_allclose(
        lp_largest_total(zeros, c["other"], *room),
        self_employed_plan_limit(c["other"], *room),
        rtol=1e-9,
        atol=1e-6,
    )
    np.testing.assert_allclose(
        lp_largest_total(c["this"], c["other"], *room),
        self_employed_plan_limit(c["this"] + c["other"], *room),
        rtol=1e-9,
        atol=1e-6,
    )


def test_line_9_examples():
    """Form 7206 line 9 in the YAML tests' Cases 22, 26 and 27."""
    room_2023 = (PLAN_RATE, 66_000, 22_500, 0)
    room_2026 = (PLAN_RATE, 72_000, 24_500, 0)
    cases = [
        # Case 22: the partnership's plan carries its whole earned income.
        (15_000, 18_587.045, 9_293.5225, room_2023, 5_706.4775),
        # ... and the Schedule C plan can carry everything.
        (15_000, 9_293.5225, 18_587.045, room_2023, 0),
        # Case 26.
        (35_652.227, 46_467.6125, 9_293.5225, room_2026, 28_217.409),
        # Case 27.
        (40_484.8587, 39_962.14675, 39_962.14675, room_2026, 8_515.1413),
    ]
    for total, this, other, room, expected in cases:
        model = plan_deduction_attributable_to_business(
            np.array([total]), np.array([this]), np.array([other]), *room
        )
        assert abs(model[0] - expected) < 0.001
