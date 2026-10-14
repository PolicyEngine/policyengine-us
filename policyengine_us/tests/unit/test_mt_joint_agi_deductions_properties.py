"""Properties of Montana's AGI-based deductions on a joint (single-column) return.

From 2021 to 2023 the Form 2 Itemized Deductions Schedule (line 1b) and the
Standard Deduction Worksheet (line 1) both take Montana AGI from Form 2 page 1,
line 14. Single, head of household and joint returns report that line in one
column, so a joint return pools both spouses' income. The model retains its
existing convention of flooring that pooled Montana AGI at zero. From 2024
Form 2 line 2 takes federal itemized deductions (Worksheet A), so the medical
floor applies to federal AGI.

The deterministic tests evaluate every point of an input grid in one vectorized
simulation; Hypothesis adds generated batches that check the same invariants:

- 2021-2023: the medical deduction is max(0, expenses - 7.5% of the return's
  Montana AGI), and the standard deduction is 20% of that AGI held between the
  filing status minimum and maximum;
- moving an income item between spouses preserves both deductions when the
  return's applicable AGI and medical expenses are held fixed;
- each deduction is held once, by the head;
- the medical deduction lies between zero and the medical expenses;
- for a single filer the joint and separate variants agree;
- from 2024 the medical deduction is the federal medical expense deduction,
  including where Montana AGI differs from federal AGI.

Hypothesis also generates arbitrary couples over 2021-2026 to check these
invariants beyond the deterministic grid, with witnesses for losses, dependent
expenses, the standard-deduction interior, and senior Montana subtractions.
Sources: 2022 Form 2, PDF p. 7, and 2024 instructions, PDF p. 15:
https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7
https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15
"""

import itertools

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st

from policyengine_us import Simulation

MEDICAL_FLOOR = 0.075  # Itemized Deductions Schedule line 1c
STANDARD_RATE = 0.2  # Standard Deduction Worksheet line 2

HEAD_WAGES = [0, 30_000, 60_000, 100_000]
SPOUSE_SELF_EMPLOYMENT = [-50_000, -20_000, 0, 40_000]
MEDICAL = [0, 2_000, 10_000, 30_000]
# Where the spouse's self-employment income is recorded: on the spouse, or
# moved to the head. The return's income is the same either way.
SPLITS = ["spouse", "head"]
CHILD_MEDICAL = [None, 1_500]  # no child, or a dependent child's expenses
COUPLE_GRID = list(
    itertools.product(
        HEAD_WAGES, SPOUSE_SELF_EMPLOYMENT, MEDICAL, SPLITS, CHILD_MEDICAL
    )
)
SINGLE_GRID = list(
    itertools.product([0, 20_000, 100_000], [-10_000, 0], MEDICAL, [40, 70])
)
STATE_YEARS = [2021, 2022, 2023]
FEDERAL_YEARS = [2024, 2025]
YEARS = STATE_YEARS + FEDERAL_YEARS


def every_year(value):
    return {year: value for year in YEARS}


@pytest.fixture(scope="module")
def grid():
    """One simulation holding every couple and single-filer grid point."""
    people, tax_units, households = {}, {}, {}
    unit_of_person, role = [], []
    for i, (wages, se, medical, split, child) in enumerate(COUPLE_GRID):
        head, spouse = f"c{i}_head", f"c{i}_spouse"
        people[head] = {
            "age": every_year(40),
            "employment_income": every_year(wages),
            "self_employment_income": every_year(se if split == "head" else 0),
            "other_medical_expenses": every_year(medical),
        }
        people[spouse] = {
            "age": every_year(40),
            "self_employment_income": every_year(se if split == "spouse" else 0),
        }
        members = [head, spouse]
        if child is not None:
            name = f"c{i}_child"
            people[name] = {
                "age": every_year(10),
                "is_tax_unit_dependent": every_year(True),
                "other_medical_expenses": every_year(child),
            }
            members.append(name)
        unit_of_person += [i] * len(members)
        role += ["head", "spouse", "dependent"][: len(members)]
        tax_units[f"c{i}"] = {"members": members}
        households[f"c{i}"] = {"members": members, "state_code": every_year("MT")}
    for j, (wages, se, medical, age) in enumerate(SINGLE_GRID):
        name = f"s{j}"
        people[name] = {
            "age": every_year(age),
            "employment_income": every_year(wages),
            "self_employment_income": every_year(se),
            "other_medical_expenses": every_year(medical),
        }
        unit_of_person.append(len(COUPLE_GRID) + j)
        role.append("head")
        tax_units[name] = {"members": [name]}
        households[name] = {"members": [name], "state_code": every_year("MT")}
    sim = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    return sim, np.array(unit_of_person), np.array(role)


N_COUPLES = len(COUPLE_GRID)
COUPLES = slice(0, N_COUPLES)
SINGLES = slice(N_COUPLES, None)


def per_unit(sim, variable, year, unit):
    """Sum a person-level variable to its tax unit, in grid order."""
    return np.bincount(unit, weights=sim.calculate(variable, year))


def montana_agi_reference(sim, year):
    # The grid has no Montana additions or subtractions before 2024, so page 1
    # line 14 is the return's federal AGI, floored at zero like PE's.
    return np.maximum(sim.calculate("adjusted_gross_income", year), 0)


def twin_pairs():
    """Index pairs of couples that differ only in which spouse has the item."""
    index = {point: i for i, point in enumerate(COUPLE_GRID)}
    return np.array(
        [
            (index[(w, se, m, "spouse", c)], index[(w, se, m, "head", c)])
            for w, se, m, split, c in COUPLE_GRID
            if split == "spouse"
        ]
    ).T


@pytest.mark.parametrize("year", STATE_YEARS)
def test_premises(grid, year):
    sim, unit, _ = grid
    filing_status = sim.calculate("filing_status", year).decode_to_str()
    assert set(filing_status[COUPLES]) == {"JOINT"}
    assert set(filing_status[SINGLES]) == {"SINGLE"}
    np.testing.assert_allclose(
        sim.calculate("mt_agi_joint", year), montana_agi_reference(sim, year)
    )
    # Moving the item between spouses does not change the return's AGI...
    spouse_side, head_side = twin_pairs()
    agi = sim.calculate("adjusted_gross_income", year)
    np.testing.assert_allclose(agi[spouse_side], agi[head_side])
    # ...but it does change the sum of each spouse's AGI floored at zero, so
    # the grid reaches the cases where pooling matters.
    summed_individual = per_unit(sim, "mt_agi_indiv", year, unit)
    assert np.any(summed_individual[COUPLES] > agi[COUPLES] + 1)


@pytest.mark.parametrize("year", STATE_YEARS)
def test_medical_floor_uses_the_return_montana_agi(grid, year):
    sim, unit, role = grid
    expenses = sim.calculate("itemized_medical_expenses", year)
    expected = np.maximum(
        expenses - MEDICAL_FLOOR * montana_agi_reference(sim, year), 0
    )
    deduction = per_unit(sim, "mt_medical_expense_deduction_joint", year, unit)
    np.testing.assert_allclose(deduction, expected, atol=0.01)
    held = sim.calculate("mt_medical_expense_deduction_joint", year)
    assert np.all(held[role != "head"] == 0)
    assert np.all(deduction >= 0)
    assert np.all(deduction <= expenses + 0.01)
    spouse_side, head_side = twin_pairs()
    np.testing.assert_allclose(deduction[spouse_side], deduction[head_side])
    assert deduction.max() > 0
    # Adding each spouse's Montana AGI after flooring it at zero would change
    # the deduction somewhere on the grid.
    summed_individual = per_unit(sim, "mt_agi_indiv", year, unit)
    unpooled = np.maximum(expenses - MEDICAL_FLOOR * summed_individual, 0)
    assert np.any(np.abs(unpooled - expected) > 1)


@pytest.mark.parametrize("year", STATE_YEARS)
def test_standard_deduction_uses_the_return_montana_agi(grid, year):
    sim, unit, role = grid
    p = sim.tax_benefit_system.parameters(
        f"{year}-01-01"
    ).gov.states.mt.tax.income.deductions.standard
    filing_status = sim.calculate("filing_status", year).decode_to_str()
    minimum = p.floor[filing_status]
    maximum = p.cap[filing_status]
    expected = np.clip(
        STANDARD_RATE * montana_agi_reference(sim, year), minimum, maximum
    )
    deduction = per_unit(sim, "mt_standard_deduction_joint", year, unit)
    np.testing.assert_allclose(deduction, expected, atol=0.01)
    held = sim.calculate("mt_standard_deduction_joint", year)
    assert np.all(held[role != "head"] == 0)
    spouse_side, head_side = twin_pairs()
    np.testing.assert_allclose(deduction[spouse_side], deduction[head_side])
    # Some returns fall between the minimum and maximum.
    assert np.any((deduction > minimum + 1) & (deduction < maximum - 1))
    # Adding each spouse's Montana AGI after flooring it at zero would change
    # the deduction somewhere on the grid.
    summed_individual = per_unit(sim, "mt_agi_indiv", year, unit)
    unpooled = np.clip(STANDARD_RATE * summed_individual, minimum, maximum)
    assert np.any(np.abs(unpooled - expected) > 1)


@pytest.mark.parametrize("year", STATE_YEARS)
def test_single_filer_joint_and_separate_variants_agree(grid, year):
    sim, unit, _ = grid
    for joint, separate in [
        ("mt_medical_expense_deduction_joint", "mt_medical_expense_deduction_indiv"),
        ("mt_standard_deduction_joint", "mt_standard_deduction_indiv"),
    ]:
        np.testing.assert_allclose(
            per_unit(sim, joint, year, unit)[SINGLES],
            per_unit(sim, separate, year, unit)[SINGLES],
            atol=0.01,
        )


@pytest.mark.parametrize("year", FEDERAL_YEARS)
def test_from_2024_the_federal_medical_deduction_carries_through(grid, year):
    sim, unit, role = grid
    federal = sim.calculate("medical_expense_deduction", year)
    deduction = per_unit(sim, "mt_medical_expense_deduction_joint", year, unit)
    np.testing.assert_allclose(deduction, federal, atol=0.01)
    held = sim.calculate("mt_medical_expense_deduction_joint", year)
    assert np.all(held[role != "head"] == 0)
    # The grid includes returns whose Montana AGI differs from federal AGI
    # (the subtraction for taxpayers 65 and older) and that deduct expenses.
    montana_agi = sim.calculate("mt_agi_joint", year)
    federal_agi = np.maximum(sim.calculate("adjusted_gross_income", year), 0)
    assert np.any((montana_agi < federal_agi - 1) & (deduction > 0))


GENERATED_YEARS = list(range(2021, 2027))
# Keep wages plus positive self-employment below the 2021 Social Security
# wage base. Moving SE earnings to the wage earner would otherwise change
# the SE-tax deduction, changing federal AGI for a reason unrelated to MT.
GENERATED_COUPLES = st.lists(
    st.tuples(
        st.integers(min_value=0, max_value=100_000),
        st.integers(min_value=-40_000, max_value=40_000),
        st.integers(min_value=0, max_value=50_000),
        st.one_of(st.none(), st.integers(min_value=0, max_value=10_000)),
        st.sampled_from([40, 70]),
        st.sampled_from([40, 70]),
    ),
    min_size=1,
    max_size=6,
)


def generated_couple_simulation(points):
    """Batch arbitrary situations with both placements of each income item."""
    people, tax_units, households = {}, {}, {}
    unit_of_person = []

    def all_years(value):
        return {year: value for year in GENERATED_YEARS}

    for point_index, (wages, se, medical, child, head_age, spouse_age) in enumerate(
        points
    ):
        for split_index, split in enumerate(["spouse", "head"]):
            unit = 2 * point_index + split_index
            head, spouse = f"h{unit}", f"s{unit}"
            people[head] = {
                # Keep medical expenses fixed when moving income between seniors;
                # modeled Medicare premiums/MSP would otherwise change the premise.
                "medicare_enrolled": all_years(False),
                "age": all_years(head_age),
                "employment_income": all_years(wages),
                "self_employment_income": all_years(se if split == "head" else 0),
                "other_medical_expenses": all_years(medical),
            }
            people[spouse] = {
                "medicare_enrolled": all_years(False),
                "age": all_years(spouse_age),
                "self_employment_income": all_years(se if split == "spouse" else 0),
            }
            members = [head, spouse]
            if child is not None:
                name = f"c{unit}"
                people[name] = {
                    "age": all_years(10),
                    "is_tax_unit_dependent": all_years(True),
                    "other_medical_expenses": all_years(child),
                }
                members.append(name)
            unit_of_person.extend([unit] * len(members))
            tax_units[f"t{unit}"] = {"members": members}
            households[f"hh{unit}"] = {
                "members": members,
                "state_code": all_years("MT"),
            }
    simulation = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )
    return simulation, np.array(unit_of_person)


@settings(max_examples=8, deadline=None)
@given(points=GENERATED_COUPLES)
def test_generated_joint_deduction_invariants(points):
    # Fixed witnesses in every randomized batch prevent vacuous passes and
    # retain the inherited zero-clipping convention. Their pre-2024 medical
    # arithmetic is (10,000 + 1,500) - 7.5% * (100,000 - 20,000) = 5,500;
    # 10,000 - 7.5% * max(-20,000, 0) = 10,000. The standard witness is
    # 20% * (50,000 - 10,000) = 8,000, inside the 2022 joint bounds.
    witnesses = [
        (100_000, -20_000, 10_000, 1_500, 70, 40),
        (0, -20_000, 10_000, None, 40, 40),
        (50_000, -10_000, 0, None, 40, 40),
        # The older second adult is the model's head, despite input order.
        (0, 0, 0, None, 40, 70),
    ]
    sim, unit = generated_couple_simulation(points + witnesses)
    for year in GENERATED_YEARS:
        federal_agi = sim.calculate("adjusted_gross_income", year)
        np.testing.assert_allclose(federal_agi[::2], federal_agi[1::2], atol=0.02)
        assert set(sim.calculate("filing_status", year).decode_to_str()) == {"JOINT"}
        # Head selection follows the oldest eligible adult, not input order.
        is_head = sim.calculate("is_tax_unit_head", year)
        assert np.all(np.bincount(unit, weights=is_head) == 1)
        # There is no Social Security income in these situations. The
        # signed federal person amounts, state additions, and subtractions
        # are therefore pooled before applying the existing zero floor.
        pooled_agi = np.maximum(
            per_unit(sim, "adjusted_gross_income_person", year, unit)
            + per_unit(sim, "mt_additions", year, unit)
            - per_unit(sim, "mt_subtractions", year, unit),
            0,
        )
        montana_agi = sim.calculate("mt_agi_joint", year)
        np.testing.assert_allclose(montana_agi, pooled_agi, atol=0.02)
        np.testing.assert_allclose(montana_agi[::2], montana_agi[1::2], atol=0.02)

        expenses = sim.calculate("itemized_medical_expenses", year)
        # Dependent medical expenses are part of the return's expenses.
        # Medicare premiums are disabled to hold expenses fixed across twins.
        np.testing.assert_allclose(
            expenses, per_unit(sim, "other_medical_expenses", year, unit), atol=0.02
        )
        np.testing.assert_allclose(expenses[::2], expenses[1::2], atol=0.02)
        medical = per_unit(sim, "mt_medical_expense_deduction_joint", year, unit)
        standard = per_unit(sim, "mt_standard_deduction_joint", year, unit)
        for variable, values in [
            ("mt_medical_expense_deduction_joint", medical),
            ("mt_standard_deduction_joint", standard),
        ]:
            # Exactly the head carries the amount; no spouse or dependent
            # can duplicate the return's deduction.
            assert np.all(sim.calculate(variable, year)[~is_head] == 0)
            np.testing.assert_allclose(values[::2], values[1::2], atol=0.02)
        assert np.all(medical >= 0)
        assert np.all(medical <= expenses + 0.02)

        if year < 2024:
            np.testing.assert_allclose(
                montana_agi, np.maximum(federal_agi, 0), atol=0.02
            )
            np.testing.assert_allclose(
                medical,
                np.maximum(expenses - MEDICAL_FLOOR * montana_agi, 0),
                atol=0.02,
            )
            p = sim.tax_benefit_system.parameters(
                f"{year}-01-01"
            ).gov.states.mt.tax.income.deductions.standard
            filing_status = sim.calculate("filing_status", year).decode_to_str()
            minimum, maximum = p.floor[filing_status], p.cap[filing_status]
            np.testing.assert_allclose(
                standard,
                np.clip(STANDARD_RATE * montana_agi, minimum, maximum),
                atol=0.02,
            )
            assert np.all(standard >= minimum - 0.02)
            assert np.all(standard <= maximum + 0.02)
            summed_individual = per_unit(sim, "mt_agi_indiv", year, unit)
            assert np.any(summed_individual > montana_agi + 1)
        else:
            np.testing.assert_allclose(
                medical, sim.calculate("medical_expense_deduction", year), atol=0.02
            )
            np.testing.assert_allclose(
                medical,
                np.maximum(expenses - MEDICAL_FLOOR * np.maximum(federal_agi, 0), 0),
                atol=0.02,
            )
            np.testing.assert_allclose(
                standard, sim.calculate("standard_deduction", year), atol=0.02
            )
            # Every batch includes a senior with positive expenses and
            # enough income for the MT subtraction to change the AGI.
            assert np.any((montana_agi < federal_agi - 1) & (medical > 0))
