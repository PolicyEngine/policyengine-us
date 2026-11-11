"""Property tests for state provisions that read railroad retirement benefits.

IRC 86(d)(1)(B) makes the tier 1 social security equivalent benefit a social
security benefit for federal tax, and states write their provisions around
that amount, title II Social Security, or both. These properties mostly swap
one benefit for the other and compare the two households. Invariants, for
every input the strategies draw:

S1. Moving all of a filer's benefits from title II to tier 1, with or without
    the rest of a railroad annuity, leaves federal AGI unchanged and never
    raises state income tax before refundable credits, with two intended
    exceptions. Form 4884 and MCL 206.30 reduce Michigan's retirement and
    standard deduction limits by the railroad benefits that federal AGI
    includes, and not by Social Security. Minnesota's elderly or disabled
    subtraction (Minn. Stat. 290.0802) reduces its base by "pension, annuity,
    or disability benefits included in federal gross income but not subject to
    state taxation" in full (subd. 1(c)) and takes them out of the adjusted
    gross income it halves (subd. 1(a)), so taxable tier 1 benefits shrink the
    subtraction where taxable title II benefits would not; S1 lets Minnesota's
    tax rise by its top rate times the subtraction lost.
S2. In the states that tax no filer's Social Security in 2025, the swap leaves
    state income tax unchanged. Michigan is excepted as in S1. After
    refundable credits, Idaho is a model gap, not an exception: 7 CFR
    273.9(b)(2)(ii) counts railroad retirement benefits as SNAP unearned
    income, the model's SNAP income list leaves them out
    (PolicyEngine/policyengine-us#10551), so the swap can make a household
    SNAP eligible, and Idaho denies its grocery credit for SNAP months. The
    test skips that check until the SNAP list counts railroad benefits. Before
    refundable credits, Idaho stays neutral.
S3. Each state income test in INCOME_TESTS counts tier 1 like title II: the
    swap leaves the test's income unchanged, for any wages, pensions and rest
    of a railroad annuity.
S4. Each pension deduction in PENSION_CAPS shrinks equally for title II and
    tier 1, because its law reduces the cap by both: the swap leaves the
    deduction unchanged, with or without the rest of a railroad annuity.
    Benefits can only reduce the deduction, and do reduce it when the pension
    exceeds the cap and no other railroad benefits use the cap up.
S5. Minnesota's Social Security subtraction (Minn. Stat. 290.0132, subd. 26)
    stays between zero and the taxable title II benefits. Adding the taxable
    tier 1 benefits that the model subtracts with the rest of the railroad
    annuity, as Schedule M1M line 17 does, total relief reaches at least what
    the same benefits would get as title II.
S6. Adding railroad benefits (tier 1, and the taxable and tax-free rest of the
    annuity) never lowers a state's base: state AGI, or state taxable income
    where the reported AGI includes the benefits. A state that subtracted the
    benefits twice would fail. The households have no title II benefits: the
    model splits the section 86 amount between title II and tier 1 in
    proportion to the benefits, so as tier 1 grows, part of the taxable
    amount moves off title II, which some states tax. They have no Part B
    premium either: the benefits can end a Medicare Savings Program's payment
    of it, and Idaho and Ohio subtract premiums the filer pays. Oregon
    subtracts federal income tax inside its AGI (ORS 316.680(1)(b)), which
    the benefits raise, so it is skipped, and Colorado and South Carolina are
    skipped while the standard deduction absorbs part of the benefits, as in
    I4 of test_railroad_retirement_taxation.py. Each Social Security
    subtraction in SOCIAL_SECURITY_SUBTRACTIONS stays at or below the taxable
    title II benefits, so with the taxable railroad benefits subtracted once,
    the two never exceed what federal AGI includes from both.
D1. Differential: walking the 2025 Schedule M1M line 12 worksheet step by step,
    with its published amounts and Form 1040 lines taken from the model, gives
    the model's subtraction for every filing status. At steps 12 and 13 the
    walk adds half of line 6b, the taxable benefits, as Minn. Stat. 290.0132,
    subd. 26(i) defines provisional income, where the worksheet takes half of
    line 6a.

The model estimates state income tax paid from withholding, and its
state_withholding_agi counts title II benefits but not railroad benefits. That
estimate feeds the deduction for state and local taxes, which has nothing to
do with how a state treats the benefits, so S1 and S2 set its input to zero
for both households.

The swap households take up no SSI. Oklahoma's supplement rounds "the monthly
amount of each income source" to the nearest dollar (OAC 317:35-5-42(i)), and
the swap turns two payments, title II and the rest of a railroad annuity, into
one railroad payment. The supplement, which Oklahoma's gross income and sales
tax credit count, can then move by a dollar a month: $26.50 and $416.50 round to
$444, and $443 stays $443. That rounding has nothing to do with how a state
treats the benefits.

YAML tests pin worked examples; these properties quantify over amounts, filing
status and every state, which YAML cannot.
"""

import math

from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.tests.test_railroad_retirement_taxation import (
    FEDERAL_AGI_STATES,
    FEDERAL_TAXABLE_INCOME_STATES,
    INCOME_TAX_STATES,
    STATE_BASE_EXCEPTIONS,
    calc,
    situation,
    tolerance,
)

YEAR = 2025
TITLE_II = "social_security_retirement"
TIER_1 = "railroad_social_security_equivalent_benefits"
TIER_2 = "taxable_railroad_pension_benefits"
TAX_FREE = "tax_exempt_railroad_pension_benefits"
PARAMETERS = system.parameters(f"{YEAR}-01-01")

# The Idaho skip in S2 ends once the SNAP income list counts tier 1 benefits,
# alone or in the railroad_benefits total. The swap gives both households the
# same rest of the annuity, so only tier 1 separates them.
SNAP_UNEARNED = set(PARAMETERS.gov.usda.snap.income.sources.unearned)
SNAP_COUNTS_RAILROAD = bool({TIER_1, "railroad_benefits"} & SNAP_UNEARNED)

MN_RATES = PARAMETERS.gov.states.mn.tax.income.rates
MN_TOP_RATE = max(
    getattr(MN_RATES, status).rates[-1]
    for status in ("single", "joint", "head_of_household", "separate")
)

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

# Each subtracts Social Security benefits that federal AGI includes. The model
# subtracts the taxable tier 1 benefits with the rest of the railroad annuity
# (taxable_railroad_benefits, 45 U.S.C. 231m(a)), so none of these may reach
# them.
SOCIAL_SECURITY_SUBTRACTIONS = [
    ("CO", "co_social_security_subtraction_indv"),
    ("CT", "ct_social_security_benefit_adjustment"),
    ("MD", "md_socsec_subtraction_amount"),
    ("MN", "mn_social_security_subtraction"),
    ("NE", "ne_social_security_subtraction"),
    ("NM", "nm_social_security_income_exemption"),
    ("RI", "ri_social_security_modification"),
    ("WV", "wv_social_security_benefits_subtraction"),
]

S6_STATES = [state for state in INCOME_TAX_STATES if state != "OR"]

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
# The rest of a railroad annuity, often absent.
tier_2s = st.one_of(st.just(0), st.integers(min_value=1, max_value=40_000))
tax_frees = st.one_of(st.just(0), st.integers(min_value=1, max_value=5_000))


def couple(head, joint, age):
    """Return the head alone, or the head and a spouse with no income."""
    return [head, {"age": age, "role": "spouse"}] if joint else [head]


def swap_simulation(states, age, earnings, pension, amount, joint, tier_2, tax_free):
    """Build one Simulation with a title II and a tier 1 household per state."""
    households = [
        (
            state,
            couple(
                {
                    "age": age,
                    "employment_income": earnings,
                    "taxable_private_pension_income": pension,
                    TIER_2: tier_2,
                    TAX_FREE: tax_free,
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
    for person in built["people"].values():
        person["takes_up_ssi_if_eligible"] = {YEAR: False}
    return Simulation(situation=built)


def by_household(simulation, variable):
    return simulation.calculate(variable, YEAR, map_to="household").astype(float)


def by_tax_unit(simulation, variable, year):
    return simulation.calculate(variable, year, map_to="tax_unit").astype(float)


@settings(max_examples=8, deadline=None)
@given(
    age=ages,
    earnings=wages,
    pension=pensions,
    amount=benefits,
    joint=st.booleans(),
    tier_2=tier_2s,
    tax_free=tax_frees,
)
# Minnesota: $1,000 of the $2,000 is taxable, so the tier 1 household's
# Schedule M1R reduction is $9,750 (1,000 + 1,000 + half of 30,000 - 14,500)
# against $9,250, and its $9,600 base leaves no subtraction against $350.
@example(
    age=72, earnings=0, pension=30_000, amount=2_000, joint=False, tier_2=0, tax_free=0
)
def test_s1_s2_swapping_title_ii_for_tier_1(
    age, earnings, pension, amount, joint, tier_2, tax_free
):
    simulation = swap_simulation(
        INCOME_TAX_STATES, age, earnings, pension, amount, joint, tier_2, tax_free
    )
    agi = calc(simulation, "adjusted_gross_income")
    before_refundable = calc(simulation, "state_income_tax_before_refundable_credits")
    after_refundable = calc(simulation, "state_income_tax")
    elderly_subtraction = calc(simulation, "mn_elderly_disabled_subtraction")
    allowed = tolerance(earnings + pension + amount + tier_2 + tax_free)
    for index, state in enumerate(INCOME_TAX_STATES):
        title_ii, tier_1 = 2 * index, 2 * index + 1
        assert abs(agi[tier_1] - agi[title_ii]) <= allowed, state
        change = before_refundable[tier_1] - before_refundable[title_ii]
        if state == "MN":
            lost = elderly_subtraction[title_ii] - elderly_subtraction[tier_1]
            assert change <= allowed + MN_TOP_RATE * max(0, lost), (state, change)
        elif state not in INTENDED_INCREASE:
            assert change <= allowed, (state, change)
        if state in NEUTRAL_STATES:
            assert abs(change) <= allowed, (state, change)
            if state != "ID" or SNAP_COUNTS_RAILROAD:
                change = after_refundable[tier_1] - after_refundable[title_ii]
                assert abs(change) <= allowed, (state, change)


@settings(max_examples=15, deadline=None)
@given(
    age=ages,
    earnings=wages,
    pension=pensions,
    amount=benefits,
    joint=st.booleans(),
    tier_2=tier_2s,
    tax_free=tax_frees,
)
# Oklahoma: with SSI taken up, the supplement's rounding of each monthly source
# moved ok_gross_income by $12 (title II $12,312, tier 1 $12,324).
@example(
    age=67, earnings=0, pension=0, amount=318, joint=False, tier_2=0, tax_free=4_998
)
def test_s3_income_tests_count_tier_1_like_title_ii(
    age, earnings, pension, amount, joint, tier_2, tax_free
):
    states = [state for state, _ in INCOME_TESTS]
    simulation = swap_simulation(
        states, age, earnings, pension, amount, joint, tier_2, tax_free
    )
    allowed = tolerance(earnings + pension + amount + tier_2 + tax_free)
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
    tier_2=tier_2s,
    tax_free=tax_frees,
)
def test_s4_pension_caps_shrink_alike(age, pension, amount, joint, tier_2, tax_free):
    annuity = {TIER_2: tier_2, TAX_FREE: tax_free}
    households = [
        (
            state,
            couple(
                {"age": age, "taxable_public_pension_income": pension}
                | annuity
                | benefit,
                joint,
                age,
            ),
        )
        for state, _ in PENSION_CAPS
        for benefit in ({TITLE_II: amount}, {TIER_1: amount}, {})
    ]
    simulation = Simulation(situation=situation(households))
    allowed = tolerance(pension + amount + tier_2 + tax_free)
    for index, (state, variable) in enumerate(PENSION_CAPS):
        deduction = by_household(simulation, variable)
        title_ii, tier_1, neither = deduction[3 * index : 3 * index + 3]
        assert abs(tier_1 - title_ii) <= allowed, (state, title_ii, tier_1)
        assert tier_1 <= neither + allowed, (state, tier_1, neither)
        if pension == BINDING_PENSION and tier_2 + tax_free == 0:
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


@settings(max_examples=8, deadline=None)
@given(
    age=ages,
    earnings=wages,
    pension=pensions,
    tier_1=amounts,
    tier_2=tier_2s,
    tax_free=tax_frees,
    joint=st.booleans(),
)
# $22,350 of the tier 1 benefits are taxable; a Connecticut or Rhode Island
# Social Security worksheet that took them from Form 1040 line 6b would
# subtract them a second time.
@example(
    age=70, earnings=0, pension=40_000, tier_1=30_000, tier_2=0, tax_free=0, joint=False
)
def test_s6_railroad_benefits_never_lower_state_bases(
    age, earnings, pension, tier_1, tier_2, tax_free, joint
):
    head = {
        "age": age,
        "employment_income": earnings,
        "taxable_private_pension_income": pension,
        "medicare_part_b_enrolled": False,
    }
    railroad = {TIER_1: tier_1, TIER_2: tier_2, TAX_FREE: tax_free}
    spouse = {"age": age, "role": "spouse", "medicare_part_b_enrolled": False}
    households = [
        (state, [member] + ([spouse] if joint else []))
        for state in S6_STATES
        for member in (head, head | railroad)
    ]
    built = situation(households)
    for unit in built["tax_units"].values():
        unit["state_and_local_sales_or_income_tax"] = {YEAR: 0}
    simulation = Simulation(situation=built)
    agi = calc(simulation, "taxsim_state_agi")
    taxable_income = calc(simulation, "taxsim_state_taxable_income")
    federal_taxable_income = calc(simulation, "taxable_income")
    allowed = tolerance(earnings + pension + tier_1 + tier_2 + tax_free)
    for index, state in enumerate(S6_STATES):
        without, with_railroad = 2 * index, 2 * index + 1
        floored = federal_taxable_income[without] <= 0
        if state in FEDERAL_TAXABLE_INCOME_STATES and floored:
            continue
        base = taxable_income if state in FEDERAL_AGI_STATES else agi
        before, after = base[without], base[with_railroad]
        assert after >= before - allowed, (state, before, after)


@settings(max_examples=25, deadline=None)
@given(
    age=ages,
    earnings=wages,
    pension=pensions,
    title_ii=benefits,
    tier_1=benefits,
    tier_2=tier_2s,
    tax_free=tax_frees,
    joint=st.booleans(),
)
@example(
    age=70,
    earnings=0,
    pension=40_000,
    title_ii=10_000,
    tier_1=30_000,
    tier_2=0,
    tax_free=0,
    joint=False,
)
def test_s6_social_security_subtractions_stay_within_taxable_title_ii(
    age, earnings, pension, title_ii, tier_1, tier_2, tax_free, joint
):
    head = {
        "age": age,
        "employment_income": earnings,
        "taxable_private_pension_income": pension,
        TITLE_II: title_ii,
        TIER_1: tier_1,
        TIER_2: tier_2,
        TAX_FREE: tax_free,
    }
    households = [
        (state, couple(head, joint, age)) for state, _ in SOCIAL_SECURITY_SUBTRACTIONS
    ]
    simulation = Simulation(situation=situation(households))
    taxable_title_ii = calc(simulation, "tax_unit_taxable_social_security")
    allowed = tolerance(earnings + pension + title_ii + tier_1 + tier_2 + tax_free)
    for index, (state, variable) in enumerate(SOCIAL_SECURITY_SUBTRACTIONS):
        subtraction = by_tax_unit(simulation, variable, YEAR)[index]
        assert subtraction >= -allowed, (state, variable, subtraction)
        assert subtraction <= taxable_title_ii[index] + allowed, (
            state,
            variable,
            subtraction,
            taxable_title_ii[index],
        )


def schedule_m1m_line_12_2025(
    status, agi, line_9, line_6b, line_2a, schedule_1_line_26, tier_1
):
    """Walk the 2025 worksheet for Schedule M1M line 12, one filer at a time.

    Steps 12 and 13 add half of Form 1040 line 6a, all benefits received;
    Minn. Stat. 290.0132, subd. 26(i) adds "one-half of the taxable Social
    Security benefits", so the walk takes half of line 6b there. Tier 1
    benefits reach line 17 in the model, so this returns line 12 less any tier
    1 benefits. The worksheet's steps 26 to 29 do that above the threshold. At
    or below it line 12 takes all of line 6b, and line 17 then leaves those
    benefits out. Schedule 1 line 21 is zero for these filers.
    """
    threshold, increment, income_amount, maximum = M1M_2025[status]
    step_27 = max(line_6b - tier_1, 0)
    if agi <= threshold:
        return step_27
    step_4 = min(math.ceil((agi - threshold) / increment), 10)
    step_7 = step_4 * 0.1 * line_6b
    step_8 = max(line_6b - step_7, 0)
    step_11 = line_9 - line_6b
    step_15 = step_11 + line_6b * 0.5 + line_2a
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
        line_6b=taxable_title_ii + taxable_tier_1,
        line_2a=exempt_interest,
        schedule_1_line_26=form_line("above_the_line_deductions"),
        tier_1=taxable_tier_1,
    )
    actual = form_line("mn_social_security_subtraction")
    allowed = tolerance(earnings + self_employment + pension + title_ii + tier_1)
    assert abs(actual - expected) <= allowed, (actual, expected)
