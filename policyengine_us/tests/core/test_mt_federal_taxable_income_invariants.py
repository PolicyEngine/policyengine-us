"""Vectorized and metamorphic checks of Montana Form 2, 2024 onward.

The household arithmetic examples belong in the variable-named YAML tests.
This module exercises behavior YAML cannot express: person-to-tax-unit
conservation, QBI and medical-expense twins, and an isolated placement reform.
One baseline population covers all three years; one reform population moves
the state-income-tax adjustment between line 2 and Schedule I. Both use the
already initialized country policy; the Simulation constructor gives the
reform its own parameter tree, variables, entities, and calculation receipts.
Hypothesis draws from cached medical twins, without constructing new models.

For each year (2026 is a statutory inference pending a Montana form):
I1. Line 3 is max(0, AGI - exemptions - federal deductions excluding QBI
    and, only when the adjustment belongs on line 2, excluding the addback).
I2. The addback is nonnegative, bounded by state income tax and itemized
    deductions over the standard deduction, and zero for nonitemizers and
    general-sales-tax electors.
I3. Standard filers keep their federally elected deduction type.
I4. Removing state income tax cannot reduce itemized deductions below the
    standard deduction when the federal itemized total starts above it.
I5. Line 7 is max(0, line 3 + additions - subtractions), held by the head.
I6. Changing only the claimed QBI deduction leaves Montana income unchanged.
I7. Moving the state-income-tax adjustment from line 2 to Schedule I leaves
    line 7 unchanged when the unadjusted federal starting income is positive.
I8. Above the federal zero floor, Montana line 3 equals federal taxable
    income PLUS QBI PLUS the addback when placed on line 2. Removing an
    amount from deductions increases income; the addback sign is positive.
I9. All four repealed Montana itemization helpers are zero for every person.
I10. More medical expenses cannot raise Montana taxable income, except when
    the federal election changes to itemizing with itemized total below the
    standard deduction. Explicit elections exercise that intended exception.

The federal election is pinned after calculating Schedule A and the federal
standard deduction, before any income deductions are cached. Ordinary rows
elect the larger deduction. The exception row explicitly switches to a
smaller itemized deduction: in 2024, wages $50,000 and state income tax $1,000
give $35,400 Montana income with medical expenses $1,000 and the standard
deduction; medical expenses $5,000 give Schedule A $2,250 and Montana income
$47,750 if the filer elects to itemize. This is permitted election behavior,
not a claim that the federal optimizer chooses that election. The YAML tests
retain coverage of the model's endogenous federal itemization decision.
"""

import itertools

import numpy as np
import pytest
from hypothesis import HealthCheck, example, find, given, settings
from hypothesis import strategies as st
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.system import system


YEARS = (2024, 2025, 2026)
MEDICAL = (0, 1_000, 5_000, 16_000, 20_000, 40_000)
QBID = (0, 10_000)
ATOL = 0.01
RTOL = 1e-6  # Float32 spacing at the grid's highest income exceeds a cent.

# These rows include both federal deduction types, both SALT elections,
# capped SALT, the standard-deduction limit on the addback, wagering losses,
# a negative withholding estimate, and deductions on both spouses.
SCENARIOS = (
    dict(wages=100_000, sit=5_000),
    dict(wages=60_000, sit=3_000, real_estate=3_000, mortgage=9_000),
    dict(
        joint=True,
        wages=300_000,
        sit=15_000,
        real_estate=8_000,
        mortgage=20_000,
        charity=5_000,
    ),
    dict(wages=50_000, age=66, sit=2_000),
    dict(
        joint=True,
        wages=600_000,
        sit=35_000,
        real_estate=12_000,
        mortgage=20_000,
        charity=10_000,
    ),
    dict(
        wages=100_000,
        sit=3_000,
        sales=8_000,
        local_sales=1_000,
        real_estate=3_000,
        mortgage=20_000,
    ),
    dict(
        wages=100_000,
        sit=5_000,
        local_income=4_000,
        real_estate=8_000,
        mortgage=20_000,
    ),
    dict(
        wages=100_000,
        sit=-500,
        local_income=1_500,
        real_estate=3_000,
        mortgage=20_000,
    ),
    dict(
        wages=100_000,
        sit=5_000,
        mortgage=10_000,
        winnings=10_000,
        losses=15_000,
    ),
    dict(joint=True, wages=60_000, sit=2_000, treasury_interest=1_000),
    dict(wages=0, sit=0),
    dict(wages=3_000, sit=5_000, real_estate=2_000),
    # Above the 37% bracket with a phased-down SALT cap: exercises the 2026
    # federal itemized limitation (26 U.S.C. 68) and the 2025+ SALT phase-down.
    dict(
        wages=1_000_000,
        sit=60_000,
        real_estate=15_000,
        mortgage=20_000,
        charity=50_000,
    ),
    # Keep last: EXCEPTION_PAIR indexes the forced-election row.
    dict(wages=50_000, sit=1_000, forced_election=True),
)
GRID = tuple(itertools.product(range(len(SCENARIOS)), MEDICAL, QBID))
INDEX = {point: i for i, point in enumerate(GRID)}
QBI_PAIRS = np.array(
    [
        (INDEX[(s, m, 0)], INDEX[(s, m, 10_000)])
        for s, m in itertools.product(range(len(SCENARIOS)), MEDICAL)
    ]
)
MEDICAL_PAIRS = tuple(
    (INDEX[(s, low, q)], INDEX[(s, high, q)])
    for s, q in itertools.product(range(len(SCENARIOS)), QBID)
    for low, high in zip(MEDICAL, MEDICAL[1:])
)
EXCEPTION_PAIR = (
    INDEX[(len(SCENARIOS) - 1, 1_000, 0)],
    INDEX[(len(SCENARIOS) - 1, 5_000, 0)],
)
LEGACY = (
    "mt_itemized_deductions_joint",
    "mt_itemized_deductions_indiv",
    "mt_itemized_deductions_for_federal_itemization_joint",
    "mt_itemized_deductions_for_federal_itemization_indiv",
)
TAX_UNIT_OUTPUTS = (
    "adjusted_gross_income",
    "exemptions",
    "taxable_income_deductions",
    "taxable_income_deductions_if_not_itemizing",
    "qualified_business_income_deduction",
    "taxable_income",
    "standard_deduction",
    "itemized_taxable_income_deductions",
    "itemized_taxable_income_deductions_reduction",
    "wagering_losses_deduction",
    "salt",
    "salt_deduction",
    "salt_cap",
    "state_withheld_income_tax",
    "local_income_tax",
    "state_sales_tax",
    "local_sales_tax",
    "mt_state_income_tax_addback",
    "mt_federal_deductions",
    "mt_federal_taxable_income",
)
PERSON_OUTPUTS = (
    "mt_taxable_income_joint",
    "mt_state_income_tax_addition",
    "mt_additions",
    "mt_subtractions",
)


def _every_year(value):
    return {year: value for year in YEARS}


def _situation():
    people, tax_units, households, member_groups = {}, {}, {}, {}
    for i, (scenario_index, medical, qbid) in enumerate(GRID):
        row = SCENARIOS[scenario_index]
        head = f"head_{i}"
        members = [head]
        people[head] = {
            "age": _every_year(row.get("age", 40)),
            "employment_income": _every_year(row["wages"]),
            "other_medical_expenses": _every_year(medical),
            "home_mortgage_interest": _every_year(row.get("mortgage", 0)),
            "real_estate_taxes": _every_year(row.get("real_estate", 0)),
            "charitable_cash_donations": _every_year(row.get("charity", 0)),
            "gambling_winnings": _every_year(row.get("winnings", 0)),
            "gambling_losses": _every_year(row.get("losses", 0)),
        }
        if row.get("joint", False):
            spouse = f"spouse_{i}"
            members.append(spouse)
            people[spouse] = {
                "age": _every_year(40),
                "taxable_interest_income": _every_year(row.get("treasury_interest", 0)),
                "us_govt_interest_person": _every_year(row.get("treasury_interest", 0)),
            }
        tax_units[f"unit_{i}"] = {
            "members": members,
            "state_withheld_income_tax": _every_year(row["sit"]),
            "local_income_tax": _every_year(row.get("local_income", 0)),
            "state_sales_tax": _every_year(row.get("sales", 0)),
            "local_sales_tax": _every_year(row.get("local_sales", 0)),
            "qualified_business_income_deduction": _every_year(qbid),
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": _every_year("MT"),
        }
        member_groups[f"group_{i}"] = {"members": members}
    # Core places the entire population in one group for any omitted entity.
    # These households have only a head and optional spouse, so the same
    # member lists are valid, isolated family, SPM, and marital units.
    return {
        "people": people,
        "tax_units": tax_units,
        "households": households,
        "families": member_groups,
        "spm_units": member_groups,
        "marital_units": member_groups,
    }


def _run(situation, reform=None):
    # Supplying the shipped policy avoids rebuilding and reprocessing the
    # entire country for the reform. Simulation shares read-only baseline
    # policy and clones it before applying a supplied reform, isolating both
    # parameter writes and SPM receipts (SPMSimulationMixin's public path).
    sim = Simulation(tax_benefit_system=system, situation=situation, reform=reform)
    out = {}
    for year in YEARS:
        line6 = sim.calculate(
            "itemized_taxable_income_deductions", year
        ) + sim.calculate("wagering_losses_deduction", year)
        standard = sim.calculate("standard_deduction", year)
        itemizes = line6 > standard
        for i, (scenario, medical, _) in enumerate(GRID):
            if SCENARIOS[scenario].get("forced_election", False):
                itemizes[i] = medical >= 5_000
        sim.set_input("tax_unit_itemizes", year, itemizes)
        out[year] = {
            name: np.asarray(sim.calculate(name, year), dtype=float)
            for name in TAX_UNIT_OUTPUTS + PERSON_OUTPUTS + LEGACY
        }
        out[year]["itemizes"] = itemizes
        out[year]["filing_status"] = sim.calculate(
            "filing_status", year
        ).decode_to_str()
        out[year]["head"] = np.asarray(
            sim.calculate("is_tax_unit_head", year), dtype=bool
        )
        out[year]["unit"] = sim.populations["tax_unit"].members_entity_id
        out[year]["reduces_deduction"] = sim.tax_benefit_system.parameters(
            year
        ).gov.states.mt.tax.income.additions.state_income_tax_reduces_federal_deduction
    return out


@pytest.fixture(scope="module")
def grid_results():
    """Read-only result arrays; baseline and reform caches remain independent."""
    situation = _situation()
    baseline = _run(situation)
    reform = Reform.from_dict(
        {
            "gov.states.mt.tax.income.additions.state_income_tax_reduces_federal_deduction": {
                "2024-01-01.2024-12-31": False,
                "2025-01-01.2026-12-31": True,
            }
        },
        country_id="us",
    )
    changed = _run(situation, reform=reform)
    for year in YEARS:
        assert (
            system.parameters(
                year
            ).gov.states.mt.tax.income.additions.state_income_tax_reduces_federal_deduction
            == baseline[year]["reduces_deduction"]
        )
    return baseline, changed


def _sum_people(run, name):
    return np.bincount(run["unit"], weights=run[name], minlength=len(GRID))


def _close(actual, expected):
    np.testing.assert_allclose(actual, expected, atol=ATOL, rtol=RTOL)


@pytest.mark.parametrize("year", YEARS)
def test_form2_invariants_and_grid_coverage(grid_results, year):
    baseline, changed = grid_results
    run = baseline[year]
    agi = run["adjusted_gross_income"]
    exemptions = run["exemptions"]
    deductions = run["taxable_income_deductions"]
    qbid = run["qualified_business_income_deduction"]
    addback = run["mt_state_income_tax_addback"]
    line6 = run["itemized_taxable_income_deductions"] + run["wagering_losses_deduction"]
    standard = run["standard_deduction"]
    itemizes = run["itemizes"]
    on_line2 = run["reduces_deduction"]
    line2 = deductions - qbid - (addback if on_line2 else 0)
    line3 = run["mt_federal_taxable_income"]
    income = _sum_people(run, "mt_taxable_income_joint")
    excess = np.maximum(0, line6 - standard)
    sit = np.maximum(0, run["state_withheld_income_tax"])
    sales_elected = sit + run["local_income_tax"] < (
        run["state_sales_tax"] + run["local_sales_tax"]
    )

    # I1: both the federal-deduction bridge and the Form 2 line-3 identity.
    _close(run["mt_federal_deductions"], line2)
    _close(line3, np.maximum(0, agi - exemptions - line2))

    # I2: only claimed state income tax can be added back.
    assert np.all(addback >= 0)
    assert np.all(addback <= np.minimum(sit, excess) + ATOL)
    assert np.all(addback[~itemizes | sales_elected] == 0)

    # I3: the standard filer keeps the federal deduction type and extras.
    _close(
        run["mt_federal_deductions"][~itemizes],
        (run["taxable_income_deductions_if_not_itemizing"] - qbid)[~itemizes],
    )

    # I4: the worksheet reduction cannot cross the standard-deduction floor.
    above_standard = itemizes & (line6 >= standard)
    assert np.all((line6 - addback)[above_standard] >= standard[above_standard] - ATOL)

    # I5: Form 2 line 7 is conserved across people and held by the head.
    _close(
        income,
        np.maximum(
            0,
            line3
            + _sum_people(run, "mt_additions")
            - _sum_people(run, "mt_subtractions"),
        ),
    )
    assert np.all(run["mt_taxable_income_joint"][~run["head"]] == 0)
    assert np.all(run["mt_state_income_tax_addition"][~run["head"]] == 0)
    _close(
        _sum_people(run, "mt_state_income_tax_addition"),
        np.zeros_like(addback) if on_line2 else addback,
    )

    # I6: QBI twins differ in federal taxable income, never in Montana income.
    zero_qbi, claimed_qbi = QBI_PAIRS.T
    assert np.all(qbid[claimed_qbi] > qbid[zero_qbi])
    _close(income[zero_qbi], income[claimed_qbi])
    assert np.any(run["taxable_income"][zero_qbi] > run["taxable_income"][claimed_qbi])

    # I7: placement equivalence before the unadjusted line-3 zero floor.
    positive_start = agi - exemptions - (deductions - qbid) >= 0
    assert np.any(positive_start & (addback > 0))
    assert changed[year]["reduces_deduction"] != on_line2
    changed_income = _sum_people(changed[year], "mt_taxable_income_joint")
    _close(income[positive_start], changed_income[positive_start])

    # I7b: below the floor the placements differ, in one direction only.
    # 2025 Form 2 floors line 3 at zero BEFORE the Schedule I line 4
    # addition, so placing the addback there never yields less income than
    # removing it inside line 2 (the revised 2024 Worksheet A).
    as_addition = changed_income if on_line2 else income
    on_line_two = income if on_line2 else changed_income
    assert np.all(as_addition >= on_line_two - ATOL)
    floor_binds = ~positive_start & (addback > 0)
    assert np.any(floor_binds & (as_addition > on_line_two + ATOL))

    # I8: the sign of a line-2 adjustment is positive in taxable income.
    federal_above_floor = agi - exemptions - deductions >= 0
    _close(
        line3[federal_above_floor],
        (run["taxable_income"] + qbid + (addback if on_line2 else 0))[
            federal_above_floor
        ],
    )

    # I9: repealed helpers vanish for heads and spouses alike.
    for name in LEGACY:
        assert np.all(run[name] == 0), name

    # Year-specific guards prevent properties from passing on empty subsets.
    joint = np.array([SCENARIOS[s].get("joint", False) for s, _, _ in GRID])
    assert np.any(joint) and np.any(~joint)
    assert np.all(run["filing_status"][joint] == "JOINT")
    assert np.all(run["filing_status"][~joint] == "SINGLE")
    assert np.any(itemizes) and np.any(~itemizes)
    assert np.any(run["salt"] > run["salt_cap"])
    assert np.any((addback > 0) & (addback < sit) & np.isclose(addback, excess))
    assert np.any(itemizes & sales_elected & (run["salt_deduction"] > 0))
    assert np.any(run["wagering_losses_deduction"] > 0)
    if year >= 2025:
        # OBBBA SALT cap phase-down (26 U.S.C. 164(b)(7)) reaches the floor.
        assert np.any(np.isclose(run["salt_cap"], 10_000))
    if year == 2026:
        # The federal itemized limitation (26 U.S.C. 68, from 2026) binds,
        # and I1-I5 above already held on those rows.
        assert np.any(run["itemized_taxable_income_deductions_reduction"] > 0)
    assert np.any(_sum_people(run, "mt_subtractions") > 0)
    assert np.any(~run["head"])


def _check_medical_pair(run, pair):
    low, high = pair
    income = _sum_people(run, "mt_taxable_income_joint")
    line6 = run["itemized_taxable_income_deductions"] + run["wagering_losses_deduction"]
    flipped_below_standard = (
        not run["itemizes"][low]
        and run["itemizes"][high]
        and line6[high] < run["standard_deduction"][high]
    )
    if not flipped_below_standard:
        assert income[high] <= income[low] + ATOL + RTOL * income[low], pair
    return flipped_below_standard, income[high] > income[low] + ATOL


@settings(
    max_examples=30,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(year=st.sampled_from(YEARS), pair=st.sampled_from(MEDICAL_PAIRS))
@example(year=2024, pair=EXCEPTION_PAIR)
def test_medical_monotonicity_with_elected_type_exception(grid_results, year, pair):
    """Hypothesis shrinks violating twins without rebuilding a simulation."""
    _check_medical_pair(grid_results[0][year], pair)


@pytest.mark.parametrize("year", YEARS)
def test_medical_grid_is_monotone_except_documented_election(grid_results, year):
    run = grid_results[0][year]
    results = [_check_medical_pair(run, pair) for pair in MEDICAL_PAIRS]
    assert any(exception and increase for exception, increase in results)
    assert _check_medical_pair(run, EXCEPTION_PAIR) == (True, True)
    if year == 2024:
        # Minimize the election exception on the cached grid, with no extra
        # model construction: $1,000 -> $5,000 medical expenses, QBI zero.
        smallest_exception = find(
            st.sampled_from(MEDICAL_PAIRS),
            lambda pair: _check_medical_pair(run, pair)[1],
            settings=settings(max_examples=200, deadline=None, derandomize=True),
        )
        assert smallest_exception == EXCEPTION_PAIR
        income = _sum_people(run, "mt_taxable_income_joint")
        low, high = EXCEPTION_PAIR
        _close(income[[low, high]], np.array([35_400, 47_750]))
