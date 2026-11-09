"""Property tests for state provisions that read railroad retirement benefits.

IRC 86(d)(1)(B) makes the tier 1 social security equivalent benefit a social
security benefit for federal tax, and states write their provisions around
that amount, title II Social Security, or both. These properties mostly swap
one benefit for the other and compare the two households. Invariants, for
every input the strategies draw:

S1. Moving all of a filer's benefits from title II to tier 1 leaves federal
    AGI unchanged and never raises state income tax before refundable credits.
    Michigan is an intended exception: Form 4884 and MCL 206.30 reduce its
    retirement and standard deduction limits by the railroad benefits that
    federal AGI includes, and not by Social Security.
S2. In the states that tax no filer's Social Security in 2025, the swap leaves
    state income tax unchanged. Michigan is excepted as in S1. Idaho's grocery
    credit is excepted after refundable credits: the model's SNAP income lists
    no railroad benefits, so the swap can make a household SNAP eligible, and
    Idaho denies the credit for SNAP months. Before refundable credits, Idaho
    stays neutral.
S3. Each state income test in INCOME_TESTS counts tier 1 like title II: the
    swap leaves the test's income unchanged, for any wages and pensions.
S4. Each pension deduction in PENSION_CAPS shrinks equally for title II and
    tier 1, because its law reduces the cap by both: the swap leaves the
    deduction unchanged. Benefits can only reduce the deduction, and do reduce
    it when the pension exceeds the cap.
S5. Minnesota's Social Security subtraction (Minn. Stat. 290.0132, subd. 26)
    stays between zero and the taxable title II benefits. Adding the taxable
    tier 1 benefits that the model subtracts with the rest of the railroad
    annuity, as Schedule M1M line 17 does, total relief reaches at least what
    the same benefits would get as title II.
D1. Differential: walking the 2025 Schedule M1M line 12 worksheet step by step,
    with its published amounts and Form 1040 lines taken from the model, gives
    the model's subtraction for every filing status.

The model estimates state income tax paid from withholding, and its
state_withholding_agi counts title II benefits but not railroad benefits. That
estimate feeds the deduction for state and local taxes, which has nothing to
do with how a state treats the benefits, so S1 and S2 set its input to zero
for both households.

YAML tests pin worked examples; these properties quantify over amounts, filing
status and every state, which YAML cannot.
"""

import math

from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.tests.test_railroad_retirement_taxation import (
    INCOME_TAX_STATES,
    calc,
    situation,
    tolerance,
)

YEAR = 2025
TITLE_II = "social_security_retirement"
TIER_1 = "railroad_social_security_equivalent_benefits"

# States whose tax in 2025 can reach title II benefits: their own Social
# Security worksheets and limits or, in Missouri, retirement benefits of
# filers under 62 (Form MO-A Section C).
TAXES_SOCIAL_SECURITY = {"CO", "CT", "MN", "MO", "MT", "NM", "RI", "UT", "VT", "WV"}

# Form 4884 and MCL 206.30 reduce Michigan's limits by taxable railroad
# benefits, so tier 1 can cost a filer more than title II would.
INTENDED_INCREASE = {"MI"}

NEUTRAL_STATES = {
    state
    for state in INCOME_TAX_STATES
    if state not in TAXES_SOCIAL_SECURITY | INTENDED_INCREASE
}

# Each of these counts tier 1 railroad benefits with Social Security benefits
# in full, or (Pennsylvania) both at the same fraction, whether or not federal
# AGI includes them. The YAML test beside each variable quotes its law.
INCOME_TESTS = [
    ("CO", "co_modified_agi"),
    ("MA", "ma_scb_total_income"),
    ("ME", "me_sales_and_property_tax_fairness_credit_income"),
    ("MI", "mi_household_resources"),
    ("MN", "mn_homestead_credit_refund_household_income"),
    ("MO", "mo_ptc_gross_income"),
    ("MT", "mt_elderly_homeowner_or_renter_credit_gross_household_income"),
    ("ND", "nd_renters_refund_income"),
    ("NM", "nm_modified_gross_income"),
    ("NY", "ny_household_gross_income"),
    ("OK", "ok_gross_income"),
    ("PA", "pa_property_tax_or_rent_rebate_income"),
    ("RI", "ri_property_tax_household_income"),
    ("UT", "ut_homeowner_renter_relief_household_income"),
    ("VT", "vt_renter_credit_countable_tax_exempt_ss"),
    ("WA", "wa_pte_combined_disposable_income"),
    ("WI", "wi_homestead_income"),
    ("WV", "wv_gross_household_income"),
]

# Idaho Code 63-3022A(3), 36 M.R.S. 5122(2)(M-2)(1)(a)(ii) and Md. Tax-General
# 10-209(b)(2).
PENSION_CAPS = [
    ("ID", "id_retirement_benefits_deduction"),
    ("MD", "md_pension_subtraction_amount"),
    ("ME", "me_pension_income_deduction"),
]

# Exceeds every 2025 cap in PENSION_CAPS, joint filers' included.
BINDING_PENSION = 100_000

# Schedule M1M worksheet for line 12, 2025: the steps 2, 4, 20 and 23 amounts.
M1M_2025 = {
    "SINGLE": (84_490, 4_000, 69_250, 4_560),
    "HEAD_OF_HOUSEHOLD": (84_490, 4_000, 69_250, 4_560),
    "JOINT": (108_320, 4_000, 88_630, 5_840),
    "SURVIVING_SPOUSE": (108_320, 4_000, 88_630, 5_840),
    "SEPARATE": (54_160, 2_000, 44_315, 2_920),
}

ages = st.sampled_from((45, 58, 62, 67, 72))
wages = st.integers(min_value=0, max_value=200_000)
pensions = st.integers(min_value=0, max_value=60_000)
benefits = st.integers(min_value=1, max_value=60_000)
amounts = st.integers(min_value=0, max_value=60_000)


def couple(head, joint, age):
    """Return the head alone, or the head and a spouse with no income."""
    return [head, {"age": age, "role": "spouse"}] if joint else [head]


def swap_simulation(states, age, earnings, pension, amount, joint):
    """Build one Simulation with a title II and a tier 1 household per state."""
    households = [
        (
            state,
            couple(
                {
                    "age": age,
                    "employment_income": earnings,
                    "taxable_private_pension_income": pension,
                    label: amount,
                },
                joint,
                age,
            ),
        )
        for state in states
        for label in (TITLE_II, TIER_1)
    ]
    built = situation(households)
    for unit in built["tax_units"].values():
        unit["state_and_local_sales_or_income_tax"] = {YEAR: 0}
    return Simulation(situation=built)


def by_household(simulation, variable):
    return simulation.calculate(variable, YEAR, map_to="household").astype(float)


def by_tax_unit(simulation, variable, year):
    return simulation.calculate(variable, year, map_to="tax_unit").astype(float)


@settings(max_examples=8, deadline=None)
@given(age=ages, earnings=wages, pension=pensions, amount=benefits, joint=st.booleans())
def test_s1_s2_swapping_title_ii_for_tier_1(age, earnings, pension, amount, joint):
    simulation = swap_simulation(
        INCOME_TAX_STATES, age, earnings, pension, amount, joint
    )
    agi = calc(simulation, "adjusted_gross_income")
    before_refundable = calc(simulation, "state_income_tax_before_refundable_credits")
    after_refundable = calc(simulation, "state_income_tax")
    allowed = tolerance(earnings + pension + amount)
    for index, state in enumerate(INCOME_TAX_STATES):
        title_ii, tier_1 = 2 * index, 2 * index + 1
        assert abs(agi[tier_1] - agi[title_ii]) <= allowed, state
        change = before_refundable[tier_1] - before_refundable[title_ii]
        if state not in INTENDED_INCREASE:
            assert change <= allowed, (state, change)
        if state in NEUTRAL_STATES:
            assert abs(change) <= allowed, (state, change)
            if state != "ID":
                change = after_refundable[tier_1] - after_refundable[title_ii]
                assert abs(change) <= allowed, (state, change)


@settings(max_examples=15, deadline=None)
@given(age=ages, earnings=wages, pension=pensions, amount=benefits, joint=st.booleans())
def test_s3_income_tests_count_tier_1_like_title_ii(
    age, earnings, pension, amount, joint
):
    states = [state for state, _ in INCOME_TESTS]
    simulation = swap_simulation(states, age, earnings, pension, amount, joint)
    allowed = tolerance(earnings + pension + amount)
    for index, (state, variable) in enumerate(INCOME_TESTS):
        income = by_household(simulation, variable)
        title_ii, tier_1 = income[2 * index], income[2 * index + 1]
        assert abs(tier_1 - title_ii) <= allowed, (state, variable, title_ii, tier_1)


@settings(max_examples=15, deadline=None)
@given(
    age=st.sampled_from((67, 72)),
    pension=st.one_of(
        st.integers(min_value=1_000, max_value=60_000), st.just(BINDING_PENSION)
    ),
    amount=benefits,
    joint=st.booleans(),
)
def test_s4_pension_caps_shrink_alike(age, pension, amount, joint):
    households = [
        (
            state,
            couple(
                {"age": age, "taxable_public_pension_income": pension} | benefit,
                joint,
                age,
            ),
        )
        for state, _ in PENSION_CAPS
        for benefit in ({TITLE_II: amount}, {TIER_1: amount}, {})
    ]
    simulation = Simulation(situation=situation(households))
    allowed = tolerance(pension + amount)
    for index, (state, variable) in enumerate(PENSION_CAPS):
        deduction = by_household(simulation, variable)
        title_ii, tier_1, neither = deduction[3 * index : 3 * index + 3]
        assert abs(tier_1 - title_ii) <= allowed, (state, title_ii, tier_1)
        assert tier_1 <= neither + allowed, (state, tier_1, neither)
        if pension == BINDING_PENSION:
            assert tier_1 < neither - allowed, (state, tier_1, neither)


@settings(max_examples=25, deadline=None)
@given(
    age=ages,
    earnings=wages,
    pension=pensions,
    title_ii=amounts,
    tier_1=amounts,
    joint=st.booleans(),
    year=st.sampled_from((2022, 2025)),
)
def test_s5_minnesota_subtraction_bounds(
    age, earnings, pension, title_ii, tier_1, joint, year
):
    mixed = {
        "age": age,
        "employment_income": earnings,
        "taxable_private_pension_income": pension,
        TITLE_II: title_ii,
        TIER_1: tier_1,
    }
    all_title_ii = mixed | {TITLE_II: title_ii + tier_1, TIER_1: 0}
    simulation = Simulation(
        situation=situation(
            [
                ("MN", couple(mixed, joint, age)),
                ("MN", couple(all_title_ii, joint, age)),
            ],
            year=year,
        )
    )
    subtraction = calc(simulation, "mn_social_security_subtraction", year)
    taxable_title_ii = calc(simulation, "tax_unit_taxable_social_security", year)
    taxable_tier_1 = by_tax_unit(
        simulation, "taxable_railroad_social_security_equivalent_benefits", year
    )
    allowed = tolerance(earnings + pension + title_ii + tier_1)
    assert subtraction[0] >= -allowed
    assert subtraction[0] <= taxable_title_ii[0] + allowed
    assert subtraction[0] + taxable_tier_1[0] >= subtraction[1] - allowed


def schedule_m1m_line_12_2025(
    status, agi, line_9, line_6a, line_6b, line_2a, schedule_1_line_26, tier_1
):
    """Walk the 2025 worksheet for Schedule M1M line 12, one filer at a time.

    Tier 1 benefits reach line 17 in the model, so this returns line 12 less
    any tier 1 benefits. The worksheet's steps 26 to 29 do that above the
    threshold. At or below it line 12 takes all of line 6b, and line 17 then
    leaves those benefits out. Schedule 1 line 21 is zero for these filers.
    """
    threshold, increment, income_amount, maximum = M1M_2025[status]
    step_27 = max(line_6b - tier_1, 0)
    if agi <= threshold:
        return step_27
    step_4 = min(math.ceil((agi - threshold) / increment), 10)
    step_7 = step_4 * 0.1 * line_6b
    step_8 = max(line_6b - step_7, 0)
    step_11 = line_9 - line_6b
    step_15 = step_11 + line_6a * 0.5 + line_2a
    step_19 = max(step_15 - max(schedule_1_line_26, 0), 0)
    step_21 = max(step_19 - income_amount, 0)
    step_24 = max(maximum - step_21 * 0.2, 0)
    step_28 = min(step_24, step_27)
    step_29 = max(step_8 - tier_1, 0)
    return max(step_28, step_29)


@settings(max_examples=40, deadline=None)
@given(
    status=st.sampled_from(sorted(M1M_2025)),
    age=ages,
    earnings=wages,
    self_employment=st.integers(min_value=0, max_value=80_000),
    pension=pensions,
    exempt_interest=st.integers(min_value=0, max_value=20_000),
    title_ii=amounts,
    tier_1=amounts,
)
def test_d1_minnesota_subtraction_matches_the_2025_worksheet(
    status, age, earnings, self_employment, pension, exempt_interest, title_ii, tier_1
):
    head = {
        "age": age,
        "employment_income": earnings,
        "self_employment_income": self_employment,
        "taxable_private_pension_income": pension,
        "tax_exempt_interest_income": exempt_interest,
        TITLE_II: title_ii,
        TIER_1: tier_1,
    }
    built = situation([("MN", couple(head, status == "JOINT", age))])
    built["tax_units"]["h0"]["filing_status"] = {YEAR: status}
    simulation = Simulation(situation=built)

    def form_line(variable):
        return float(by_tax_unit(simulation, variable, YEAR)[0])

    taxable_title_ii = form_line("taxable_social_security")
    taxable_tier_1 = form_line("taxable_railroad_social_security_equivalent_benefits")
    expected = schedule_m1m_line_12_2025(
        status,
        agi=form_line("adjusted_gross_income"),
        line_9=form_line("irs_gross_income"),
        line_6a=form_line("tax_unit_section_86_benefits"),
        line_6b=taxable_title_ii + taxable_tier_1,
        line_2a=exempt_interest,
        schedule_1_line_26=form_line("above_the_line_deductions"),
        tier_1=taxable_tier_1,
    )
    actual = form_line("mn_social_security_subtraction")
    allowed = tolerance(earnings + self_employment + pension + title_ii + tier_1)
    assert abs(actual - expected) <= allowed, (actual, expected)
