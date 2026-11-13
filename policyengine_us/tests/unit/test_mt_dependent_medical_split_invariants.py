"""Invariants for Montana's tax-minimizing split of dependents' medical bills.

On a 2021-2023 return where spouses file separately on the same form (status
2a), the couple may divide bills paid from a joint account that are not
attributable to one spouse in any proportion, and may elect the standard
deduction (both spouses or neither). The model treats every dependent's bill
as jointly paid, takes the head's share of those bills
(mt_dependent_medical_expense_head_share) from a closed-form candidate set to
minimize the couple's combined tax before refundable credits (Form 2 line 20 in both
columns), and picks the election (mt_tax_unit_itemizes) by the same tax.

For each couple in a seeded population of 40 per year:

1. The chosen tax is at most the tax at each of these shares when itemizing:
   all to the head, all to the spouse, the equal split, the shares at which
   each column's 7.5% floor starts to bind (computed here from the inputs,
   not read from the model), and 0.1 to 0.9. With no capital gain credit the
   minimum over all shares is at 0, 1 or where the columns' incomes balance,
   so the interior shares catch a chooser that misses the balance point.
2. The chosen tax is at most the tax with the standard deduction in both
   columns.
3. The couple's Montana tax (mt_income_tax) is at most its tax before this
   change, which counted no dependent bills and itemized when the summed
   itemized deductions exceeded the summed standard deductions.
4. Swapping which spouse is labelled head leaves the couple's tax unchanged.
5. More dependent bills never raise the couple's tax.

Properties 3 to 5 use mt_income_tax in 2022 and 2023. In 2021 they use line
20, because the 2021 income tax rebate is capped at line 20 in each column
and is left out of the choice.

Why Python rather than YAML: the properties compare generated couples with
their own variants (other shares, the other election, swapped labels, more
bills). The YAML cases pin worked examples.

Montana AGI and the other itemized deductions are inputs, so the federal
return does not enter. Core treats a formula variable supplied for some tax
units as supplied for all of them, so the forced shares and elections run in
a second simulation in which every tax unit has them.
"""

import numpy as np
import pytest

from policyengine_core.periods import period

from policyengine_us import Simulation
from policyengine_us.tools.mt_separate_return import (
    mt_separate_tax_before_refundable_credits,
)

# Dollars; the model computes in float32 and incomes reach $150,000.
TOLERANCE = 0.05
FORM_FLOOR = 0.075  # Itemized Deductions Schedule line 1c
YEARS = [2021, 2022, 2023]
EQUAL_SPLIT = 0.5


def _kinks(couple, pool):
    """The head shares at which each column's floor starts to bind."""
    room = [FORM_FLOOR * couple["agi"][i] - couple["own_medical"][i] for i in range(2)]
    if pool <= 0:
        return EQUAL_SPLIT, EQUAL_SPLIT
    head = min(max(room[0] / pool, 0.0), 1.0)
    spouse = min(max(1 - room[1] / pool, 0.0), 1.0)
    return head, spouse


def _situation(entries, year):
    """entries: (tag, couple, swapped, bills, unit inputs) per tax unit."""
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for tag, couple, swapped, dependent_bills, unit_inputs in entries:
        filers = []
        for i in (1, 0) if swapped else (0, 1):
            name = f"{tag}_filer{i}"
            people[name] = {
                "age": {year: 40},
                "is_tax_unit_head": {year: i == (1 if swapped else 0)},
                "is_tax_unit_spouse": {year: i == (0 if swapped else 1)},
                "mt_agi_indiv": {year: couple["agi"][i]},
                "other_medical_expenses": {year: couple["own_medical"][i]},
                "mt_non_medical_itemized_deductions_indiv": {
                    year: couple["other_itemized"][i]
                },
            }
            filers.append(name)
        members = list(filers)
        for j, amount in enumerate(dependent_bills):
            name = f"{tag}_child{j}"
            people[name] = {
                "age": {year: 10},
                "is_tax_unit_dependent": {year: True},
                "other_medical_expenses": {year: amount},
            }
            members.append(name)
            marital_units[f"{name}_alone"] = {"members": [name]}
        marital_units[f"{tag}_couple"] = {"members": filers}
        unit = {
            "members": members,
            "mt_agi_joint": {year: sum(couple["agi"])},
        }
        unit.update({k: {year: v} for k, v in unit_inputs.items()})
        tax_units[tag] = unit
        households[tag] = {"members": members, "state_code": {year: "MT"}}
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }


def _taxes(entries, year):
    sim = Simulation(situation=_situation(entries, year))
    unit = sim.populations["tax_unit"].members_entity_id
    n = len(entries)

    def unit_sum(name):
        values = np.asarray(sim.calculate(name, year), dtype=float)
        return np.bincount(unit, weights=values, minlength=n)

    out = {
        "line_20": unit_sum("mt_income_tax_before_refundable_credits_indiv"),
        "itemized": unit_sum("mt_itemized_deductions_indiv"),
        "standard": unit_sum("mt_standard_deduction_indiv"),
    }
    for name in ["mt_income_tax", "mt_dependent_medical_expense_head_share"]:
        out[name] = np.asarray(sim.calculate(name, year), dtype=float)
    out["couple_tax"] = out["line_20"] if year == 2021 else out["mt_income_tax"]
    return out


def _check(couples_drawn, year):
    n = len(couples_drawn)
    # First simulation: the model chooses. Variants: as drawn, labels
    # swapped, more bills, and no dependent bills (for the old election).
    free = []
    for i, c in enumerate(couples_drawn):
        more = [c["dependent_bills"][0] + c["more_bills"]] + c["dependent_bills"][1:]
        free += [
            (f"u{i}", c, False, c["dependent_bills"], {}),
            (f"s{i}", c, True, c["dependent_bills"], {}),
            (f"m{i}", c, False, more, {}),
            (f"z{i}", c, False, [0.0] * len(c["dependent_bills"]), {}),
        ]
    chosen = _taxes(free, year)
    pick = lambda k: chosen["couple_tax"][k::4]  # noqa: E731
    as_drawn, swapped, more_bills, no_bills = (pick(k) for k in range(4))
    old_itemizes = chosen["itemized"][3::4] > chosen["standard"][3::4]
    share = chosen["mt_dependent_medical_expense_head_share"][0::4]
    assert ((share >= 0) & (share <= 1)).all()

    # Second simulation: every tax unit has a forced share and election.
    forced, labels = [], []
    for i, c in enumerate(couples_drawn):
        pool = sum(c["dependent_bills"])
        head_kink, spouse_kink = _kinks(c, pool)
        for label, s in [
            ("equal", EQUAL_SPLIT),
            ("head", 1.0),
            ("spouse", 0.0),
            ("head_kink", head_kink),
            ("spouse_kink", spouse_kink),
        ] + [(f"grid{k}", k / 10) for k in range(1, 10)]:
            inputs = {
                "mt_dependent_medical_expense_head_share": s,
                "mt_tax_unit_itemizes": True,
            }
            forced.append((f"{label}{i}", c, False, c["dependent_bills"], inputs))
            labels.append(label)
        standard = {
            "mt_dependent_medical_expense_head_share": EQUAL_SPLIT,
            "mt_tax_unit_itemizes": False,
        }
        forced.append((f"standard{i}", c, False, c["dependent_bills"], standard))
        labels.append("standard")
        old = {
            "mt_dependent_medical_expense_head_share": EQUAL_SPLIT,
            "mt_tax_unit_itemizes": bool(old_itemizes[i]),
        }
        zero = [0.0] * len(c["dependent_bills"])
        forced.append((f"old{i}", c, False, zero, old))
        labels.append("old")
    fixed = _taxes(forced, year)
    per = len(labels) // n
    labels = np.array(labels[:per])
    fixed_line_20 = fixed["line_20"].reshape(n, per)
    fixed_tax = fixed["couple_tax"].reshape(n, per)

    # 1 and 2. The chosen line 20 is at most every candidate's and the
    # standard deduction's.
    candidates = labels != "old"
    assert (
        chosen["line_20"][0::4] <= fixed_line_20[:, candidates].min(axis=1) + TOLERANCE
    ).all()
    # 3. At most the tax before this change.
    assert (as_drawn <= fixed_tax[:, labels == "old"][:, 0] + TOLERANCE).all()
    # 4. Label swap.
    np.testing.assert_allclose(as_drawn, swapped, atol=TOLERANCE)
    # 5. More bills never raise the tax.
    assert (more_bills <= as_drawn + TOLERANCE).all()
    # The free choice with no dependent bills is the old return's tax or less.
    assert (no_bills <= fixed_tax[:, labels == "old"][:, 0] + TOLERANCE).all()


SEED = 20261102


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    rng = np.random.default_rng(SEED + year)
    drawn = []
    for _ in range(40):
        drawn.append(
            {
                "agi": [float(rng.integers(0, 150_001)) for _ in range(2)],
                "own_medical": [
                    float(rng.choice([0, rng.integers(1, 12_001)])) for _ in range(2)
                ],
                "other_itemized": [
                    float(rng.choice([0, rng.integers(1, 12_001)])) for _ in range(2)
                ],
                "dependent_bills": [
                    float(rng.choice([0, rng.integers(1, 40_001)]))
                    for _ in range(int(rng.integers(1, 3)))
                ],
                "more_bills": float(rng.integers(1, 10_001)),
            }
        )
    _check(drawn, year)


@pytest.mark.parametrize("year", YEARS)
def test_closed_form_matches_columns(year):
    """The closed form the choices compare equals the columns' line 20.

    Couples with wages and long-term capital gains, so the 2021-2023 capital
    gain credit (Montana's non-refundable credit) is non-zero, and the federal
    return feeds Montana AGI. A closed form that drifts from the column
    variables would make the choices minimize a tax the columns don't owe.
    """
    rng = np.random.default_rng(SEED + 10 * year)
    people, tax_units, households, marital_units = {}, {}, {}, {}
    for i in range(30):
        members = []
        for role in ("head", "spouse"):
            name = f"u{i}_{role}"
            people[name] = {
                "age": {year: 45},
                "employment_income": {year: float(rng.integers(0, 120_001))},
                "long_term_capital_gains": {year: float(rng.integers(0, 40_001))},
                "other_medical_expenses": {
                    year: float(rng.choice([0, rng.integers(1, 8_001)]))
                },
            }
            members.append(name)
        marital_units[f"u{i}_couple"] = {"members": list(members)}
        child = f"u{i}_child"
        people[child] = {
            "age": {year: 10},
            "is_tax_unit_dependent": {year: True},
            "other_medical_expenses": {year: float(rng.integers(0, 30_001))},
        }
        marital_units[f"u{i}_child_alone"] = {"members": [child]}
        members.append(child)
        tax_units[f"u{i}"] = {"members": members}
        households[f"u{i}"] = {"members": members, "state_code": {year: "MT"}}
    situation = {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "households": households,
    }
    sim = Simulation(situation=situation)
    tax_unit = sim.populations["tax_unit"]
    unit = tax_unit.members_entity_id
    n = tax_unit.count
    columns = np.bincount(
        unit,
        weights=np.asarray(
            sim.calculate("mt_income_tax_before_refundable_credits_indiv", year),
            dtype=float,
        ),
        minlength=n,
    )
    credits = np.bincount(
        unit,
        weights=np.asarray(sim.calculate("mt_non_refundable_credits", year), float),
        minlength=n,
    )
    # The guard is only meaningful if the credit is in play for most couples.
    assert (credits > 0).sum() >= n // 2
    deductions = sim.calculate("mt_deductions_indiv", year)
    closed_form = mt_separate_tax_before_refundable_credits(
        tax_unit, period(year), sim.tax_benefit_system.parameters, deductions
    )
    np.testing.assert_allclose(closed_form, columns, atol=0.01)
