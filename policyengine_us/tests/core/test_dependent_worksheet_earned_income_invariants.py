"""Invariants for earned income on the standard deduction worksheet for dependents.

The Form 1040 Standard Deduction Worksheet for Dependents starts earned income
from line 1z, and line 1a is the total of Form(s) W-2, box 1, which leaves out
elective deferrals (2025 Form 1040 instructions, PDF pages 23, 25 and 35).
`standard_deduction_worksheet_earned_income` is that amount for the head and
spouse; `basic_standard_deduction` (26 USC 63(c)(5)), `or_standard_deduction`
and `hi_deductions` use it for a filer who can be claimed as a dependent, and
`medicaid_person_is_required_to_file` reads the same earned income sources.
YAML cases pin single households; these tests check what must hold for every
input.

`test_worksheet_properties` draws batches of single and joint tax units with
Hypothesis (any mix of claimability, wages, 401(k) deferrals, self-employment
and farm income or loss, and interest, in Oregon, Hawaii or Texas) and runs
each batch, with four variants of every unit, as one simulation for 2025 and
2026. Three fixed units, the review's case (a claimed single filer with
$10,000 of wages, a $6,000 deferral and $600 of interest) in each state,
start every batch so that each property has rows to check:

1. Deferral invariance: a unit whose wages are W with a deferral D gets the
   same worksheet earned income, deductions, federal filing requirement and
   Medicaid filing requirement as a twin with wages max(W - D, 0) and no
   deferral. Only W-2 box 1 wages matter.
2. Bounds: the basic standard deduction of a unit whose head or spouse can be
   claimed is at least the section 63(c)(5)(A) amount and never more than the
   regular basic standard deduction for its filing status; for any other unit
   it is the regular amount. Hawaii's limited deduction never exceeds Hawaii's
   regular standard deduction.
3. Monotonicity: $1,000 more wages with the same deferral never lowers
   worksheet earned income or any of the three deductions, and a deferral
   $1,000 larger out of the same wages never raises them.
4. Reference: for units with wages and deferrals only, worksheet earned income
   equals the sum of max(W - D, 0) over the head and spouse, and the basic
   standard deduction of a claimable unit equals min(regular amount,
   max(63(c)(5)(A) amount, worksheet earned income + 63(c)(5)(B) amount)).
5. Table 2 (2025): for single claimable filers under 65 and not blind with
   only wages, deferrals and interest, both `tax_unit_is_required_to_file` and
   `medicaid_person_is_required_to_file` equal Publication 501 (2025), Table
   2, computed with W-2 box 1 wages as earned income.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM

YEARS = (2025, 2026)
STATES = ("OR", "HI", "TX")
VARIANTS = ("base", "twin", "raised", "deferred")
RAISE = 1_000

# Publication 501 (2025), Table 2, single dependents not 65 or older or blind:
# https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=4
TABLE_2_FLOOR = 1_350
TABLE_2_EARNED_INCOME_ADDITION = 450
TABLE_2_EARNED_INCOME_LIMIT = 15_750


def simulate(units):
    """One simulation of independent tax units, each in its own household."""
    people, tax_units, households = {}, {}, {}
    groups = {"marital_units": {}, "spm_units": {}, "families": {}}
    for index, unit in enumerate(units):
        members = [f"adult_{index}_{n}" for n in range(len(unit["adults"]))]
        for name, inputs in zip(members, unit["adults"]):
            people[name] = {
                variable: {year: value for year in YEARS}
                for variable, value in inputs.items()
            }
        tax_units[f"tax_unit_{index}"] = {
            "members": members,
            "filing_status": {year: unit["filing_status"] for year in YEARS},
            # Keep Hawaii's comparison on the standard deduction.
            "hi_itemized_deductions": {year: 0 for year in YEARS},
        }
        households[f"household_{index}"] = {
            "members": members,
            "state_code": {year: unit["state"] for year in YEARS},
        }
        for name in ("spm_units", "families"):
            groups[name][f"{name}_{index}"] = {"members": members}
        groups["marital_units"][f"marital_unit_{index}"] = {"members": members}
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            **groups,
        }
    )


def adult(claimed, wages, deferral, self_employment, farm, interest):
    return {
        "age": 30,
        "is_blind": False,
        "claimed_as_dependent_on_another_return": claimed,
        "employment_income": wages,
        "traditional_401k_contributions": deferral,
        "self_employment_income": self_employment,
        "farm_operations_income": farm,
        "taxable_interest_income": interest,
    }


def variant(unit, kind):
    """The unit, its no-deferral twin, or the unit with more wages or a larger
    deferral out of the same wages."""
    adults = []
    for person in unit["adults"]:
        person = dict(person)
        if kind == "twin":
            person["employment_income"] = max(
                person["employment_income"] - person["traditional_401k_contributions"],
                0,
            )
            person["traditional_401k_contributions"] = 0
        elif kind == "raised":
            person["employment_income"] += RAISE
        elif kind == "deferred":
            person["traditional_401k_contributions"] = min(
                person["traditional_401k_contributions"] + RAISE,
                person["employment_income"],
            )
        adults.append(person)
    return {**unit, "adults": adults}


money = st.integers(min_value=0, max_value=40_000)
loss_or_profit = st.one_of(st.just(0), st.integers(min_value=-10_000, max_value=10_000))


@st.composite
def adults(draw):
    wages = draw(money)
    deferral = draw(st.integers(min_value=0, max_value=wages))
    return adult(
        claimed=draw(st.booleans()),
        wages=wages,
        deferral=deferral,
        self_employment=draw(loss_or_profit),
        farm=draw(loss_or_profit),
        interest=draw(st.integers(min_value=0, max_value=5_000)),
    )


@st.composite
def units(draw):
    joint = draw(st.booleans())
    members = [draw(adults()) for _ in range(2 if joint else 1)]
    return {
        "filing_status": "JOINT" if joint else "SINGLE",
        "state": draw(st.sampled_from(STATES)),
        "adults": members,
    }


# Fixed units so every property has rows: the reviewer's case and its twin.
FIXED_UNITS = [
    {
        "filing_status": "SINGLE",
        "state": state,
        "adults": [adult(True, 10_000, 6_000, 0, 0, 600)],
    }
    for state in STATES
]


def head_values(simulation, units, variable, year):
    values = np.asarray(simulation.calculate(variable, year))
    first = np.cumsum([0] + [len(unit["adults"]) for unit in units])
    return values[first[:-1]]


@settings(
    max_examples=40,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(units(), min_size=1, max_size=12))
def test_worksheet_properties(drawn):
    base = FIXED_UNITS + drawn
    batch = [variant(unit, kind) for kind in VARIANTS for unit in base]
    simulation = simulate(batch)
    n = len(base)
    rows = {kind: slice(i * n, (i + 1) * n) for i, kind in enumerate(VARIANTS)}
    claimable = np.array(
        [
            any(a["claimed_as_dependent_on_another_return"] for a in unit["adults"])
            for unit in base
        ]
    )
    joint = np.array([unit["filing_status"] == "JOINT" for unit in base])
    wages_only = np.array(
        [
            all(
                a["self_employment_income"] == 0 and a["farm_operations_income"] == 0
                for a in unit["adults"]
            )
            for unit in base
        ]
    )
    hi = np.array([unit["state"] == "HI" for unit in base])
    assert (claimable & wages_only & ~joint).any()

    for year in YEARS:
        p = SYSTEM.parameters(year).gov.irs.deductions.standard
        values = {
            variable: np.asarray(simulation.calculate(variable, year))
            for variable in (
                "standard_deduction_worksheet_earned_income",
                "basic_standard_deduction",
                "standard_deduction",
                "tax_unit_is_required_to_file",
                "or_standard_deduction",
                "hi_deductions",
                "hi_standard_deduction",
            )
        }
        values["medicaid_head"] = head_values(
            simulation, batch, "medicaid_person_is_required_to_file", year
        )

        # 1. Deferral invariance.
        for variable, value in values.items():
            np.testing.assert_array_equal(
                value[rows["base"]],
                value[rows["twin"]],
                err_msg=f"{year}: {variable} depends on the deferral, not box 1",
            )

        # 2. Bounds.
        regular = np.where(joint, p.amount["JOINT"], p.amount["SINGLE"])
        basic = values["basic_standard_deduction"][rows["base"]]
        assert (basic[claimable] <= regular[claimable] + 1e-6).all(), year
        assert (basic[claimable] >= p.dependent.amount - 1e-6).all(), year
        np.testing.assert_allclose(basic[~claimable], regular[~claimable])
        hi_limited = values["hi_deductions"][rows["base"]][hi]
        hi_regular = values["hi_standard_deduction"][rows["base"]][hi]
        assert (hi_limited <= hi_regular + 1e-6).all(), year

        # 3. Monotonicity in box 1 wages, both ways.
        for variable in (
            "standard_deduction_worksheet_earned_income",
            "basic_standard_deduction",
            "or_standard_deduction",
            "hi_deductions",
        ):
            value = values[variable]
            assert (value[rows["raised"]] >= value[rows["base"]] - 1e-6).all(), (
                f"{year}: {variable} falls with more box 1 wages"
            )
            assert (value[rows["deferred"]] <= value[rows["base"]] + 1e-6).all(), (
                f"{year}: {variable} rises with a larger deferral"
            )

        # 4. Reference, for units with wages and deferrals only.
        worksheet = values["standard_deduction_worksheet_earned_income"][rows["base"]]
        expected_worksheet = np.array(
            [
                sum(
                    max(a["employment_income"] - a["traditional_401k_contributions"], 0)
                    for a in unit["adults"]
                )
                for unit in base
            ]
        )
        np.testing.assert_allclose(
            worksheet[wages_only], expected_worksheet[wages_only], atol=0.01
        )
        expected_basic = np.minimum(
            regular,
            np.maximum(
                p.dependent.amount,
                expected_worksheet + p.dependent.additional_earned_income,
            ),
        )
        rows_4 = wages_only & claimable
        np.testing.assert_allclose(basic[rows_4], expected_basic[rows_4], atol=0.01)

        # 5. Table 2 with box 1 wages as earned income (2025 amounts).
        if year == 2025:
            single = ~joint & claimable & wages_only
            person = [unit["adults"][0] for unit in base]
            earned = np.array(
                [
                    max(a["employment_income"] - a["traditional_401k_contributions"], 0)
                    for a in person
                ]
            )
            unearned = np.array([a["taxable_interest_income"] for a in person])
            expected = (
                (unearned > TABLE_2_FLOOR)
                | (earned > TABLE_2_EARNED_INCOME_LIMIT)
                | (
                    earned + unearned
                    > np.maximum(
                        TABLE_2_FLOOR,
                        np.minimum(
                            earned,
                            TABLE_2_EARNED_INCOME_LIMIT
                            - TABLE_2_EARNED_INCOME_ADDITION,
                        )
                        + TABLE_2_EARNED_INCOME_ADDITION,
                    )
                )
            )
            assert single.any()
            for variable in ("tax_unit_is_required_to_file", "medicaid_head"):
                np.testing.assert_array_equal(
                    values[variable][rows["base"]][single],
                    expected[single],
                    err_msg=f"2025: {variable} differs from Table 2 on box 1 wages",
                )
