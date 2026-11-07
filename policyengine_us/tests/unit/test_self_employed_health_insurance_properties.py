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
Schedule C income, SSTB and non-SSTB together, as one business, and bases the
line 16 plan deduction on Schedule C income, so only the Schedule C business
subtracts it.

Hypothesis draws batches of self-employed single filers and runs each batch as
one vectorized baseline simulation. Each drawn filer appears six times: with
no named plan business, again with higher premiums, and once naming each of
the four businesses. For every filer and year:

1. Reference: Schedule 1 line 15 equals half of the self-employment tax
   computed here from Schedule SE, and each limit equals a closed-form Form
   7206 computation for its plan business from that line 15 and the model's
   line 16. Without a named business, the limit is the largest of the four.
   The deduction is the smaller of line 3 and that reference limit. Line 3
   adds the drawn long-term care premiums, up to the limit for ages 41 to 50
   (line 2), to the medical premiums (line 1).
2. Differential: the limit without a named business equals the largest of the
   limits the model computes when each business is named. With property 1,
   which ties each named limit to that business's own Form 7206, one plan
   never pools the earned income of two businesses.
3. Bounds: 0 <= deduction <= line 3, and the limit is at least the Schedule
   C limit (widening the base never lowers the deduction).
4. Monotone in premiums: raising the medical premiums by d raises the
   deduction by at least 0 and at most d, and leaves the limit unchanged.
5. For a filer with no business losses whose income is wages and
   self-employment income, the deduction never takes adjusted gross income
   below the Schedule C line 10 amount before its floor at zero. That amount
   is negative only when the Schedule 1 line 16 plan deduction exceeds the
   Schedule C business's net profit less its share of line 15; otherwise
   adjusted gross income stays at or above zero. Intended: a plan under the
   farm or partnership does not subtract the Schedule C plan deduction.
6. Line 2 and Schedule A: the long-term care part is the smaller of line 2
   and what the deduction leaves after line 1, and Schedule A keeps line 3
   less the deduction, so each premium in line 3 counts once.

The model computes in float32, whose spacing passes a cent above $131,072, so
comparisons allow a relative error of 1e-6 on top of the $0.01 tolerance.
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
BUSINESSES = ["SCHEDULE_C", "SCHEDULE_F", "PARTNERSHIP", "S_CORPORATION"]
# (name prefix, named plan business, premium raise) for each copy of a filer.
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


def form_7206_limits(schedule_c, farm, partnership, s_corp, line_15, line_16):
    """Form 7206 line 13 for each plan business, with lines 15 and 16 given.

    Also returns the Schedule C line 10 amount before its floor at zero.
    """
    line_4 = {
        "SCHEDULE_C": np.maximum(schedule_c, 0),
        "SCHEDULE_F": np.maximum(farm, 0),
        "PARTNERSHIP": np.maximum(partnership, 0),
    }
    line_5 = sum(line_4.values())
    safe_line_5 = np.where(line_5 > 0, line_5, 1)
    line_10 = {}
    for business, profit in line_4.items():
        line_6 = np.where(line_5 > 0, profit / safe_line_5, 0)
        line_8 = profit - line_15 * line_6
        line_9 = line_16 if business == "SCHEDULE_C" else 0
        line_10[business] = line_8 - line_9
    line_13 = {business: np.maximum(amount, 0) for business, amount in line_10.items()}
    line_13["S_CORPORATION"] = np.maximum(s_corp, 0)
    return line_13, line_10["SCHEDULE_C"]


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

    # The model's Schedule C is SSTB and non-SSTB income together.
    schedule_c = column(filers, "schedule_c") + column(filers, "sstb")
    farm = column(filers, "farm")
    partnership = column(filers, "partnership")
    s_corp = column(filers, "s_corp")
    # S corporation wages are Social Security wages too.
    wages = column(filers, "wages") + s_corp
    long_term_care = column(filers, "long_term_care")
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
        # Line 16 does not depend on premiums or the named business.
        for prefix, _, _ in COPIES[1:]:
            close(copy(line_16, prefix), copy(line_16, "u"))
        line_13, schedule_c_line_10 = form_7206_limits(
            schedule_c,
            farm,
            partnership,
            s_corp,
            expected_line_15,
            copy(line_16, "u"),
        )
        largest = np.max(np.stack(list(line_13.values())), axis=0)
        # The reference limit for every copy, in the simulation's order.
        reference_limit = np.concatenate(
            [
                largest if business == "UNSPECIFIED" else line_13[business]
                for _, business, _ in COPIES
            ]
        )

        # 1. Reference.
        close(deduction, np.minimum(line_3, reference_limit))
        close(copy(limit, "u"), largest)
        for business in BUSINESSES:
            close(copy(limit, business.lower()), line_13[business])

        # 2. Differential: the default equals the best named business.
        named = np.stack([copy(limit, b.lower()) for b in BUSINESSES])
        close(copy(limit, "u"), named.max(axis=0))

        # 3. Bounds.
        assert np.all(deduction >= 0)
        assert at_least(line_3, deduction)
        assert at_least(copy(limit, "u"), line_13["SCHEDULE_C"])

        # 4. Monotone and 1-Lipschitz in premiums; the limit ignores premiums.
        base, raised = copy(deduction, "u"), copy(deduction, "r")
        assert at_least(raised, base)
        assert at_least(base + PREMIUM_RAISE, raised)
        close(copy(limit, "u"), copy(limit, "r"))

        # 5. Adjusted gross income floor for filers with no business losses.
        no_losses = (
            (column(filers, "schedule_c") >= 0)
            & (column(filers, "sstb") >= 0)
            & (farm >= 0)
            & (partnership >= 0)
        )
        floor = np.minimum(0, schedule_c_line_10)
        for prefix, _, _ in COPIES:
            assert at_least(copy(agi, prefix)[no_losses], floor[no_losses])

        # 6. Line 2 takes what the deduction leaves after line 1, and
        # Schedule A keeps line 3 less the deduction.
        close(
            long_term_care_part,
            np.minimum(line_2, deduction - np.minimum(premiums, deduction)),
        )
        close(schedule_a, line_3 - deduction)


money = st.integers(0, 120_000)
filer_strategy = st.fixed_dictionaries(
    {
        "schedule_c": st.one_of(
            st.sampled_from([-5_000, 0, 400, 434, 2_000, 160_000, 250_000]),
            st.integers(-20_000, 300_000),
        ),
        "sstb": st.one_of(st.just(0), st.integers(-20_000, 100_000)),
        "farm": st.one_of(st.just(0), st.integers(-30_000, 100_000)),
        "partnership": st.one_of(st.just(0), st.integers(-30_000, 100_000)),
        "s_corp": st.one_of(st.just(0), st.integers(0, 150_000)),
        "wages": st.one_of(st.just(0), st.integers(0, 250_000)),
        "plan": st.one_of(st.just(0), money),
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
        premiums=premiums,
        long_term_care=long_term_care,
    )


def test_reviewer_example_and_boundaries():
    """Fixed filers: the $2,000 example, the $400 threshold, the new bases and
    long-term care premiums."""
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
        # A plan deduction as large as the Schedule C profit, with the farm as
        # the plan business (property 5).
        filer(schedule_c=20_000, plan=20_000, farm=50_000, premiums=100_000),
        # Long-term care premiums under an S corporation plan: in 2022, line 3
        # is 6,000 + min(2,000, 850) = 6,850, above line 11.
        filer(s_corp=6_500, premiums=6_000, long_term_care=2_000),
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
