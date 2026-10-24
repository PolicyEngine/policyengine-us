"""Invariants for the filing requirement of a filer who can be claimed.

`tax_unit_is_required_to_file` gives a filer who can be claimed as a dependent
on another return the three tests of Publication 501 (2025), Table 2 (Chart B
of the Form 1040 instructions; 26 USC 6012(a)(1)(C)(i) and (f), 63(c)(5)). It
codes only the unearned income test. The earned income and gross income tests
come from comparing gross income with `standard_deduction`, which is already
the limited section 63(c)(5) deduction for these filers. Nobody else has an
unearned income test. YAML cases pin the published amounts one case at a time;
these tests check what must hold for every input, which YAML cannot state.

On a 2018-2025 joint return, section 6012(f)(2)(D) tests a claimable
spouse's income other than earned income against the section 63(c)(5)(A)
amount alone, while Table 2 adds the additional standard deduction for age or
blindness; the model follows the statute, and property 10 states it. Where
the statute and the IRS charts differ otherwise (a dependent filing
separately, and in 2026 blindness and the exact dollar), the tests below
assert nothing that depends on the difference.

`test_table_2_boundary_grid` runs one simulation of single filers on a grid of
earned and unearned income at every Table 2 threshold, a dollar under and a
dollar over, for each combination of age 65 and blindness:

1. Differential: for a filer who can be claimed, the result equals Table 2's
   three tests computed directly from its published 2025 amounts. This is the
   check that the two tests with no code of their own are still applied.
2. Differential: in 2025 it also equals `medicaid_person_is_required_to_file`,
   the other Table 2 implementation, which serves Medicaid and ACA household
   income for dependents inside a tax unit. In 2026 the rule is section
   6012(a)(1), whose treatment of blindness and the exact dollar is open, so
   the two are not compared there.
3. For a filer nobody can claim, the result depends on gross income alone: it
   is the same however that income is split between wages and interest.
4. On a 2025 joint return with no other income, where the spouse who can be
   claimed has only interest, the result is section 6012(f)(2)(D)'s unearned
   income test (over $1,350), whatever either spouse's age and blindness.
   Table 2 would add $1,600 for each of the claimed spouse's age 65 and
   blindness; the grid's amounts between $1,350 and those sums tell the two
   apart.

`test_filing_requirement_properties` draws batches of tax units with
Hypothesis (single, head of household, surviving spouse, separate and joint;
any mix of age, blindness, claimability, wages, self-employment income or
loss, interest and dividends) and runs each batch, with four variants of every
unit, as one simulation for 2025 and 2026. Every batch starts with two fixed
units, one that must file and one that need not, so that each property below
has rows to check and both answers occur; the test asserts that it does.

5. Split invariance: moving a filer's wages into interest, or interest into
   wages, never changes the result for a tax unit whose head and spouse cannot
   be claimed.
6. Monotonicity: more wages, interest or self-employment profit never turns
   "required" into "not required", for any tax unit.
7. Claimability never removes the requirement: marking the head as claimable
   never turns "required" into "not required" (filers who are not blind and
   do not file separately; see below).
8. A tax unit dependent's wages and interest never change the result: that
   income belongs on the dependent's own return.
9. Table 2 and the Medicaid implementation, as in 1 and 2, on the drawn
   single filers who can be claimed and have no self-employment income.
10. Lower bound (2025): on a single or separate return, a head or spouse
    who can be claimed and whose interest and dividends are over Table 2's
    unearned income amount for them always makes the return required. On a
    joint return the amount is section 6012(f)(2)(D)'s: the section
    63(c)(5)(A) amount, $1,350, with no addition for age or blindness.

`test_earned_income_sources_are_gross_income_sources`:

11. Every earned income source of the unearned income test is a gross income
    source. Otherwise a renamed earned source would silently count as
    unearned income.

Intended exceptions, each from the law rather than the code:

- Monotonicity does not hold for a smaller self-employment loss. A loss does
  not reduce gross income ("don't reduce your income by any losses", Form 1040
  instructions, Chart A) but it does reduce the earned income that sets the
  limited standard deduction, so a smaller loss raises the threshold and not
  the income. `test_smaller_loss_can_end_the_requirement` pins the case.
- Property 7 leaves out blind filers. Chart A does not count blindness (only
  age), while Table 2 does, so on the charts a blind filer under 65 with
  wages between the two amounts must file only if nobody can claim them. From
  2026 the model follows Chart A here: section 6012(a)(1)(B) raises the
  threshold of a filer nobody can claim for age only, while a filer who can
  be claimed keeps the standard deduction test (decision d1395).
- Property 7 also leaves out separate filers: Table 2 lets a claimable
  married dependent filing separately skip a return unless the spouse
  itemizes, while sections 6012(f) and (a)(1) require one with any gross
  income (decision d1395).
- From 2026, property 7 also fails at one dollar: gross income equal to the
  threshold of a sighted filer nobody can claim. Section 6012(a)(1)(A)
  excuses that filer only if gross income is "less than" the threshold, while
  a filer who can be claimed is tested with "in excess of" (d1395). The
  property skips those units, and
  `test_claimability_can_end_the_requirement_at_the_threshold` pins the case.
- Properties 1, 2 and 9 use wages as the only earned income. Earned income for
  the limited deduction is net of the deductible part of self-employment tax
  on the IRS worksheet, which Table 2 does not spell out.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM

YEARS = (2025, 2026)

# Publication 501 (2025), Table 2, single dependents:
# https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=4
TABLE_2_FLOOR = 1_350
TABLE_2_EARNED_INCOME_ADDITION = 450
TABLE_2_EARNED_INCOME_LIMIT = 15_750
TABLE_2_AGED_OR_BLIND_ADDITION = 2_000
# The same table, married dependents: $2,950 less $1,350.
TABLE_2_MARRIED_AGED_OR_BLIND_ADDITION = 1_600

ADULT_INCOME_INPUTS = [
    "employment_income",
    "self_employment_income",
    "taxable_interest_income",
    "qualified_dividend_income",
]
VARIANTS = ["base", "split", "raised", "claimed", "with_child"]


def table_2_single_dependent(earned, unearned, aged, blind):
    """Table 2's three tests for a single dependent, from its 2025 amounts."""
    additional = TABLE_2_AGED_OR_BLIND_ADDITION * (aged.astype(int) + blind.astype(int))
    gross = earned + unearned
    unearned_test = unearned > TABLE_2_FLOOR + additional
    earned_test = earned > TABLE_2_EARNED_INCOME_LIMIT + additional
    gross_test = gross > np.maximum(
        TABLE_2_FLOOR + additional,
        np.minimum(earned, TABLE_2_EARNED_INCOME_LIMIT - TABLE_2_EARNED_INCOME_ADDITION)
        + TABLE_2_EARNED_INCOME_ADDITION
        + additional,
    )
    return unearned_test | earned_test | gross_test


def simulate(units, **options):
    """One simulation of independent tax units; options go to Simulation.

    Each unit is {"filing_status": name, "adults": [...], "children": [...]},
    with one dict of person inputs per member. Every unit states its filing
    status: an input given to one tax unit is an input for all of them, so a
    unit left without one would take the default, SINGLE, not the status the
    model would work out.
    """
    people, tax_units, households = {}, {}, {}
    groups = {"marital_units": {}, "spm_units": {}, "families": {}}
    for index, unit in enumerate(units):
        adults = [f"adult_{index}_{n}" for n in range(len(unit["adults"]))]
        children = [f"child_{index}_{n}" for n in range(len(unit["children"]))]
        members = adults + children
        for name, inputs in zip(members, unit["adults"] + unit["children"]):
            people[name] = {
                variable: {year: value for year in YEARS}
                for variable, value in inputs.items()
            }
        tax_units[f"tax_unit_{index}"] = {
            "members": members,
            "filing_status": {year: unit["filing_status"] for year in YEARS},
        }
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {year: "TX" for year in YEARS},
        }
        for name in ("spm_units", "families"):
            groups[name][f"{name}_{index}"] = {"members": members}
        groups["marital_units"][f"marital_unit_{index}"] = {"members": adults}
        for child in children:
            groups["marital_units"][f"marital_unit_{child}"] = {"members": [child]}
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            **groups,
        },
        **options,
    )


def single_filer(age, blind, claimed, wages, interest):
    return {
        "filing_status": "SINGLE",
        "adults": [
            {
                "age": age,
                "is_blind": blind,
                "claimed_as_dependent_on_another_return": claimed,
                "employment_income": wages,
                "taxable_interest_income": interest,
            }
        ],
        "children": [],
    }


def head_values(units, name):
    return np.array([unit["adults"][0].get(name, 0) for unit in units])


def unit_totals(simulation, units, variable, year):
    """A person variable summed over the members of each unit."""
    values = np.asarray(simulation.calculate(variable, year))
    sizes = [len(unit["adults"]) + len(unit["children"]) for unit in units]
    return np.add.reduceat(values, np.cumsum([0] + sizes[:-1]))


def head_medicaid_requirement(simulation, units, year):
    """`medicaid_person_is_required_to_file` for each unit's head."""
    values = simulation.calculate("medicaid_person_is_required_to_file", year)
    first = np.cumsum([0] + [len(u["adults"]) + len(u["children"]) for u in units])
    return np.asarray(values)[first[:-1]]


def unearned_test_met(units):
    """Whether the unearned income test is met by a head or spouse who can be
    claimed (2025 amounts): Table 2's for single and separate returns, and
    section 6012(f)(2)(D)'s, with no addition for age or blindness, for joint
    returns."""
    met = []
    for unit in units:
        if unit["filing_status"] == "JOINT":
            per_condition = 0
        elif unit["filing_status"] == "SEPARATE":
            per_condition = TABLE_2_MARRIED_AGED_OR_BLIND_ADDITION
        else:
            per_condition = TABLE_2_AGED_OR_BLIND_ADDITION
        met.append(
            unit["filing_status"] in ("SINGLE", "SEPARATE", "JOINT")
            and any(
                adult["claimed_as_dependent_on_another_return"]
                and adult["taxable_interest_income"]
                + adult.get("qualified_dividend_income", 0)
                > TABLE_2_FLOOR
                + per_condition * ((adult["age"] >= 65) + adult["is_blind"])
                for adult in unit["adults"]
            )
        )
    return np.array(met)


def assert_table_2(simulation, units, required, rows, year):
    """Properties 1 and 2 (and 9) on the given rows of single claimable filers,
    in 2025."""
    assert rows.any(), "no single claimable filer to compare"
    if year != 2025:
        return
    np.testing.assert_array_equal(
        required[rows],
        head_medicaid_requirement(simulation, units, year)[rows],
        err_msg=f"{year}: differs from medicaid_person_is_required_to_file",
    )
    expected = table_2_single_dependent(
        earned=head_values(units, "employment_income"),
        unearned=head_values(units, "taxable_interest_income")
        + head_values(units, "qualified_dividend_income"),
        aged=head_values(units, "age") >= 65,
        blind=head_values(units, "is_blind").astype(bool),
    )
    np.testing.assert_array_equal(
        required[rows], expected[rows], err_msg="2025: differs from Table 2"
    )


# Every Table 2 threshold for a single dependent, a dollar under and over.
EARNED_GRID = [0, 449, 899, 900, 901, 3_000]
EARNED_GRID += [15_299, 15_300, 15_301, 15_749, 15_750, 15_751]
EARNED_GRID += [17_749, 17_750, 17_751, 19_749, 19_750, 19_751]
UNEARNED_GRID = [0, 1, 449, 450, 451, 1_349, 1_350, 1_351]
UNEARNED_GRID += [2_449, 2_450, 2_451, 3_349, 3_350, 3_351]
UNEARNED_GRID += [4_449, 4_450, 4_451, 5_349, 5_350, 5_351]
GROSS_GRID = [600, 1_351, 5_351, 15_749, 15_751, 17_751, 19_751, 21_751, 40_000]


def test_table_2_boundary_grid():
    claimable = [
        single_filer(age, blind, True, wages, interest)
        for age in (19, 65)
        for blind in (False, True)
        for wages in EARNED_GRID
        for interest in UNEARNED_GRID
    ]
    # Four ways to hold the same gross income, for a filer nobody can claim.
    splits = [
        (age, blind, gross, wages)
        for age in (40, 65)
        for blind in (False, True)
        for gross in GROSS_GRID
        for wages in (gross, 0, gross // 2, gross - 600)
    ]
    unclaimable = [
        single_filer(age, blind, False, wages, gross - wages)
        for age, blind, gross, wages in splits
    ]
    # Joint returns whose spouse can be claimed and has only interest, with
    # and without age 65 and blindness: section 6012(f)(2)(D) tests every
    # such spouse at the section 63(c)(5)(A) amount alone.
    joint = [
        {
            "filing_status": "JOINT",
            "adults": [
                {
                    "age": head_age,
                    "is_blind": head_blind,
                    "claimed_as_dependent_on_another_return": False,
                    "taxable_interest_income": 0,
                },
                {
                    "age": spouse_age,
                    "is_blind": spouse_blind,
                    "claimed_as_dependent_on_another_return": True,
                    "taxable_interest_income": interest,
                },
            ],
            "children": [],
        }
        for head_age in (45, 70, 80)
        for head_blind in (False, True)
        for spouse_age in (40, 65)
        for spouse_blind in (False, True)
        for interest in UNEARNED_GRID
    ]
    units = claimable + unclaimable + joint
    simulation = simulate(units)
    is_claimable = np.arange(len(units)) < len(claimable)
    is_joint = np.arange(len(units)) >= len(claimable) + len(unclaimable)
    is_unclaimable = ~is_claimable & ~is_joint
    for year in YEARS:
        required = np.asarray(
            simulation.calculate("tax_unit_is_required_to_file", year)
        )
        if year == 2025:
            # Property 4.
            expected = unearned_test_met(units)[is_joint]
            np.testing.assert_array_equal(required[is_joint], expected)
            assert expected.any() and not expected.all()
        # Properties 1 and 2.
        assert_table_2(simulation, units, required, is_claimable, year)
        # Property 3: one answer for each gross income, whatever the split.
        by_split = required[is_unclaimable].reshape(-1, 4)
        assert (by_split == by_split[:, :1]).all(), year
        # Both answers occur, so the property is not vacuous.
        assert by_split.any() and not by_split.all(), year
    # The grid reaches both answers of each Table 2 test.
    assert required[is_claimable].any() and not required[is_claimable].all()


boundary = st.sampled_from(sorted(set(EARNED_GRID + UNEARNED_GRID + [31_499, 31_501])))
amount = st.one_of(st.just(0), boundary, st.integers(0, 45_000))
loss = st.integers(-20_000, -1)


@st.composite
def adults(draw):
    return {
        "age": draw(st.sampled_from([19, 40, 64, 65, 80])),
        "is_blind": draw(st.booleans()),
        "claimed_as_dependent_on_another_return": draw(st.booleans()),
        "employment_income": draw(amount),
        "self_employment_income": draw(st.one_of(st.just(0), amount, loss)),
        "taxable_interest_income": draw(amount),
        "qualified_dividend_income": draw(st.one_of(st.just(0), amount)),
    }


# Fixed units at the start of every batch: a single filer who can be claimed
# with $5,000 of interest (must file; meets every property's row filter) and a
# single filer nobody can claim with $600 of interest (need not file).
ANCHORS = [
    single_filer(19, False, True, 0, 5_000),
    single_filer(40, False, False, 0, 600),
]
for anchor in ANCHORS:
    anchor["adults"][0].update(self_employment_income=0, qualified_dividend_income=0)


@st.composite
def unit_variants(draw, fixed=None):
    """A tax unit (drawn, or `fixed`) and its four variants, in VARIANTS order."""
    if fixed is None:
        status = draw(
            st.sampled_from(
                ["SINGLE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE", "SEPARATE", "JOINT"]
            )
        )
        base = {
            "filing_status": status,
            "adults": [draw(adults()) for _ in range(2 if status == "JOINT" else 1)],
            "children": [],
        }
    else:
        base = {**fixed, "adults": [dict(adult) for adult in fixed["adults"]]}

    def variant(change):
        copy = {**base, "adults": [dict(adult) for adult in base["adults"]]}
        change(copy)
        return copy

    who = draw(st.integers(0, len(base["adults"]) - 1))

    # Property 5: move part of one filer's wages into interest, or back.
    moved = draw(st.integers(1, 20_000))
    to_interest = draw(st.booleans())

    def split(unit):
        adult = unit["adults"][who]
        source, target = "employment_income", "taxable_interest_income"
        if not to_interest:
            source, target = target, source
        shift = min(moved, adult[source])
        adult[source] -= shift
        adult[target] += shift

    # Property 6: more of one nonnegative source. A smaller loss is the
    # intended exception, so a loss is left alone.
    raised_source = draw(st.sampled_from(ADULT_INCOME_INPUTS))
    increase = draw(st.integers(1, 20_000))

    def raise_income(unit):
        adult = unit["adults"][who]
        source = raised_source
        if adult[source] < 0:
            source = "taxable_interest_income"
        adult[source] += increase

    # Property 7.
    def claim_head(unit):
        # The older adult is the head; mark both when the ages tie.
        oldest = max(adult["age"] for adult in unit["adults"])
        for adult in unit["adults"]:
            if adult["age"] == oldest:
                adult["claimed_as_dependent_on_another_return"] = True

    # Property 8.
    child = {
        "age": draw(st.integers(0, 17)),
        "employment_income": draw(amount),
        "taxable_interest_income": draw(amount),
    }

    def add_child(unit):
        unit["children"] = [child]

    return [
        base,
        variant(split),
        variant(raise_income),
        variant(claim_head),
        variant(add_child),
    ]


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.tuples(*(unit_variants(fixed=anchor) for anchor in ANCHORS)),
    st.lists(unit_variants(), min_size=6, max_size=22),
)
def test_filing_requirement_properties(anchors, drawn):
    units = [unit for variants in [*anchors, *drawn] for unit in variants]
    simulation = simulate(units)
    anyone_claimable = np.array(
        [
            any(a["claimed_as_dependent_on_another_return"] for a in unit["adults"])
            for unit in units
        ]
    ).reshape(-1, len(VARIANTS))
    separate = np.array(
        [unit["filing_status"] == "SEPARATE" for unit in units]
    ).reshape(-1, len(VARIANTS))
    anyone_blind = np.array(
        [any(adult["is_blind"] for adult in unit["adults"]) for unit in units]
    ).reshape(-1, len(VARIANTS))
    # Properties 1, 2 and 9 apply to a single filer who can be claimed and has
    # wages as their only earned income.
    table_2_rows = np.array(
        [
            unit["filing_status"] == "SINGLE"
            and unit["adults"][0]["claimed_as_dependent_on_another_return"]
            and unit["adults"][0]["self_employment_income"] == 0
            for unit in units
        ]
    )
    for year in YEARS:
        flat = np.asarray(simulation.calculate("tax_unit_is_required_to_file", year))
        required = dict(zip(VARIANTS, flat.reshape(-1, len(VARIANTS)).T))
        nobody_claimable = ~anyone_claimable[:, 0]
        # Property 5.
        np.testing.assert_array_equal(
            required["split"][nobody_claimable],
            required["base"][nobody_claimable],
            err_msg=f"{year}: the earned/unearned split changed the result",
        )
        assert nobody_claimable.any()
        # Property 6.
        assert not (required["base"] & ~required["raised"]).any(), (
            f"{year}: more income ended the requirement"
        )
        assert required["base"].any() and not required["base"].all()
        # Property 7, except at the 2026 threshold (see the docstring).
        sighted = ~anyone_blind[:, 0] & ~separate[:, 0]
        ended = required["base"] & ~required["claimed"]
        if year >= 2026:
            gross_income = unit_totals(
                simulation, units, "irs_gross_income", year
            ).reshape(-1, len(VARIANTS))[:, 0]
            standard_deduction = np.asarray(
                simulation.calculate("standard_deduction", year)
            ).reshape(-1, len(VARIANTS))[:, 0]
            ended &= ~(nobody_claimable & (gross_income == standard_deduction))
        assert not ended[sighted].any(), (
            f"{year}: being claimable ended the requirement"
        )
        # Property 8.
        np.testing.assert_array_equal(
            required["with_child"],
            required["base"],
            err_msg=f"{year}: a tax unit dependent's income changed the result",
        )
        # Property 9.
        assert_table_2(simulation, units, flat, table_2_rows, year)
        # Property 10.
        if year == 2025:
            met = unearned_test_met(units)
            assert met.any()
            assert flat[met].all(), (
                "2025: a claimable filer over the unearned income amount need not file"
            )


def test_earned_income_sources_are_gross_income_sources():
    # Property 11.
    for year in YEARS:
        parameters = SYSTEM.parameters(f"{year}-01-01").gov.irs
        earned = list(
            parameters.income.filing_requirement.dependent.earned_income_sources
        )
        gross = list(parameters.gross_income.sources)
        assert earned and set(earned) <= set(gross), set(earned) - set(gross)


def test_smaller_loss_can_end_the_requirement():
    # Intended exception to monotonicity. With $2,000 of wages and a $5,000
    # loss, earned income is negative, the limited standard deduction is the
    # $1,350 floor, and $2,000 of gross income is over it. With a $100 loss,
    # earned income is $1,900 and the limited deduction is $2,350.
    units = [single_filer(19, False, True, 2_000, 0) for _ in range(2)]
    units[0]["adults"][0]["self_employment_income"] = -5_000
    units[1]["adults"][0]["self_employment_income"] = -100
    required = simulate(units).calculate("tax_unit_is_required_to_file", 2025)
    assert required.tolist() == [True, False]


def test_claimability_can_end_the_requirement_at_the_threshold():
    # Intended exception to property 7 from 2026. Nobody can claim the first
    # filer, whose $16,100 of wages equals the threshold of section
    # 6012(a)(1)(A)(i), so a return is due. The second filer can be claimed;
    # $16,100 does not exceed their standard deduction of $16,100
    # ((a)(1)(C)(i)(II) and Chart B), so no return is due (decision d1395).
    units = [single_filer(40, False, claimed, 16_100, 0) for claimed in (0, 1)]
    required = simulate(units).calculate("tax_unit_is_required_to_file", 2026)
    assert required.tolist() == [True, False]
