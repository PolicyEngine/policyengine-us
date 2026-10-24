"""Invariants for Montana's 2021-2023 medical insurance premium deduction.

The 2021-2023 Form 2 Itemized Deductions Schedule floors only line 1, medical
and dental expenses other than insurance premiums, at 7.5% of Montana AGI.
Line 2 deducts medical insurance premiums in full and line 3 long-term care
insurance premiums in full, except premiums already deducted through the
self-employed health insurance deduction, and pre-tax premiums. Former MCA
15-30-2131(1)(a)(iii)-(iv) and (1)(g). From 2024 Montana takes federal
itemized deductions, where premiums stay under the federal floor.

For the head and spouse that deduction is part of Montana AGI. Premium inputs
use payer attribution: payments for dependent coverage belong on the paying
filer's input. A dependent's own premiums and self-employed deduction belong
on the dependent's own return and do not enter the filers' premium deduction.
The properties below hold for those attributed inputs and the deduction as
modeled; they do not independently establish who paid a premium.

Why Python rather than YAML: Hypothesis generates mixed populations (single,
head of household and joint returns with dependents; premiums reported
directly, decomposed or with Medicare Part B), and every batch also holds
twins of each return whose differences are asserted. YAML cases check fixed
examples; these properties check relations between generated returns.

Each batch takes the self-employed deduction one way: derived from
self-employment income ("derived"), supplied for every person ("person"), or
supplied for every return with person amounts derived ("unit"). The mode is
per batch because core treats a formula variable supplied for some members as
an input for all of them, filling the rest with 0.

Each batch runs as one vectorized simulation holding three copies of every
tax unit: the drawn return, a twin with higher after-tax and long-term care
premiums for people whose premiums no deduction can absorb, and a twin with
no pre-tax premiums. The 7.5% rate is taken from Form 2 line 1c rather than
the model's parameters. Montana AGI and the self-employed deductions are read
from the model; they are inputs to these properties, not derived
independently. For every tax unit:

1. Accounting (2021-2023): the joint deduction is
   max(0, other expenses - 7.5% x Montana AGI) + lines 2 and 3, held by the
   head. The separate variant is max(0, own other expenses - 7.5% x own
   Montana AGI) + own lines 2 and 3 for the head and spouse; dependents hold
   nothing.
2. Premium conservation against closed forms. Per-person helpers:
   line 2 + line 3 = max(0, premiums + long-term care
   premiums - own deduction), and line 2 = premiums - min(premiums, own
   deduction). Joint return: lines 2 and 3 = max(0, filers' premiums +
   filers' long-term care premiums - the return's deduction). Only the head
   and spouse claim the per-person helpers on separate returns. Premiums are
   computed from the raw inputs. Each deduction is netted exactly once.
3. Bounds (2021-2023): premiums are never floored, so the deduction is at
   least lines 2 and 3 and at most those plus other expenses.
4. Slope (2021-2023): raising filers' after-tax or long-term care premiums
   that no deduction can absorb raises the deduction by exactly the increase.
   Raising dependent-paid premiums does not increase the filers' deduction.
   Montana AGI is unchanged by those increases (asserted).
5. Pre-tax premiums never change lines 2 or 3.
6. Line 1 base: other expenses equal federal itemized medical expenses plus
   the self-employed premiums those exclude, less the filers' premiums (the
   federal subtotal leaves out a dependent's own). Line 1 therefore tracks
   the federal definition apart from the premiums.
7. Differential (2021-2023): for single filers whose deduction is recorded
   per person, the joint and separate variants agree.
8. From 2024 the joint deduction is the federal medical expense deduction and
   the separate variant is zero.
9. Differential (seeded, 2021-2023): supplying a net Schedule A subtotal, the
   exclusion of all premiums the self-employed deduction took (medical
   first), and the long-term care premiums still inside gives the same
   Montana deduction as the computed path.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

# Dollars; the model computes in float32 and unit amounts reach about $100,000.
TOLERANCE = 0.05
FORM_FLOOR = 0.075  # Itemized Deductions Schedule line 1c
STATE_YEARS = [2021, 2022, 2023]
FEDERAL_YEAR = 2024
YEARS = STATE_YEARS + [FEDERAL_YEAR]
MODES = ["derived", "person", "unit"]
VARIANTS = ["base", "raised", "no_pre_tax"]

amount = st.one_of(st.just(0.0), st.integers(1, 15_000).map(float))
small_amount = st.one_of(st.just(0.0), st.integers(1, 5_000).map(float))
deduction_amount = st.one_of(st.just(0.0), st.integers(1, 20_000).map(float))


@st.composite
def people(draw):
    self_employed = draw(st.booleans())
    return {
        "employment_income": float(draw(st.integers(0, 150_000))),
        "self_employed": self_employed,
        "self_employment_income": (
            float(draw(st.integers(-20_000, 60_000))) if self_employed else 0.0
        ),
        # A deduction claimed on Schedule 1, line 17, used in "person" mode.
        "supplied_deduction": draw(deduction_amount),
        "premium_source": draw(st.sampled_from(["direct", "decomposed", "medicare"])),
        "premium": draw(amount),
        "part_b": draw(st.integers(0, 3_000).map(float)),
        "other_medical": draw(
            st.one_of(st.just(0.0), st.integers(1, 30_000).map(float))
        ),
        "long_term_care": draw(small_amount),
        "pre_tax": draw(small_amount),
        "premium_increase": draw(small_amount),
        "long_term_care_increase": draw(small_amount),
    }


@st.composite
def tax_units(draw):
    kind = draw(st.sampled_from(["single", "hoh", "joint", "joint_dependents"]))
    n_dependents = draw(st.integers(1, 2)) if kind in ("hoh", "joint_dependents") else 0
    return {
        "head": draw(people()),
        "spouse": draw(people()) if kind.startswith("joint") else None,
        "dependents": [draw(people()) for _ in range(n_dependents)],
        # The return's deduction, used in "unit" mode.
        "supplied_unit_deduction": draw(deduction_amount),
    }


SEED = 20261006


def _seeded_units(n=120):
    rng = np.random.default_rng(SEED)

    def maybe(high):
        return float(rng.integers(1, high + 1)) if rng.random() < 0.6 else 0.0

    def person():
        self_employed = bool(rng.random() < 0.3)
        return {
            "employment_income": float(rng.integers(0, 150_001)),
            "self_employed": self_employed,
            "self_employment_income": (
                float(rng.integers(-20_000, 60_001)) if self_employed else 0.0
            ),
            "supplied_deduction": maybe(20_000),
            "premium_source": str(rng.choice(["direct", "decomposed", "medicare"])),
            "premium": maybe(15_000),
            "part_b": float(rng.integers(0, 3_001)),
            "other_medical": maybe(30_000),
            "long_term_care": maybe(5_000),
            "pre_tax": maybe(5_000),
            "premium_increase": maybe(5_000),
            "long_term_care_increase": maybe(5_000),
        }

    units = []
    for _ in range(n):
        kind = rng.choice(["single", "hoh", "joint", "joint_dependents"])
        n_dependents = (
            int(rng.integers(1, 3)) if kind in ("hoh", "joint_dependents") else 0
        )
        units.append(
            {
                "head": person(),
                "spouse": person() if kind.startswith("joint") else None,
                "dependents": [person() for _ in range(n_dependents)],
                "supplied_unit_deduction": maybe(20_000),
            }
        )
    return units


def _entries(unit):
    entries = [("head", unit["head"])]
    if unit["spouse"] is not None:
        entries.append(("spouse", unit["spouse"]))
    return entries + [("dependent", d) for d in unit["dependents"]]


def _no_own_deduction(values, mode):
    """Whether the person's own deduction is known to be zero."""
    if mode == "person":
        return values["supplied_deduction"] == 0
    return not values["self_employed"]


def _raisable(unit, role, values, mode):
    """Whether no deduction can absorb a premium increase for this person.

    The return's deduction is pooled over the head's and spouse's premiums,
    so any filer's deduction can absorb another filer's increase.
    """
    if role == "dependent":
        return _no_own_deduction(values, mode)
    filers = [v for r, v in _entries(unit) if r != "dependent"]
    if not all(_no_own_deduction(v, mode) for v in filers):
        return False
    return mode != "unit" or unit["supplied_unit_deduction"] == 0


def _increases(unit, role, values, mode, variant):
    if variant != "raised" or not _raisable(unit, role, values, mode):
        return 0.0, 0.0
    return values["premium_increase"], values["long_term_care_increase"]


def _person_inputs(unit, role, values, mode, variant):
    premium_increase, long_term_care_increase = _increases(
        unit, role, values, mode, variant
    )
    premium = values["premium"] + premium_increase
    source = values["premium_source"]
    inputs = {
        "age": 10 if role == "dependent" else 40,
        "is_tax_unit_head": role == "head",
        "is_tax_unit_spouse": role == "spouse",
        "is_tax_unit_dependent": role == "dependent",
        "employment_income": values["employment_income"],
        "is_self_employed": values["self_employed"],
        "self_employment_income": values["self_employment_income"],
        "other_medical_expenses": values["other_medical"],
        "long_term_health_insurance_premiums": values["long_term_care"]
        + long_term_care_increase,
        "pre_tax_health_insurance_premiums": (
            0.0 if variant == "no_pre_tax" else values["pre_tax"]
        ),
        "health_insurance_premiums": premium if source == "direct" else 0.0,
        "health_insurance_premiums_without_medicare_part_b": (
            0.0 if source == "direct" else premium
        ),
        "medicare_enrolled": source == "medicare",
        "medicare_part_b_premium": values["part_b"] if source == "medicare" else 0.0,
    }
    if mode == "person":
        inputs["self_employed_health_insurance_ald_person"] = values[
            "supplied_deduction"
        ]
    return inputs


def _expected_premium(unit, role, values, mode, variant):
    """Premiums counted as federal medical expenses, from the inputs alone."""
    premium = values["premium"] + _increases(unit, role, values, mode, variant)[0]
    if values["premium_source"] == "direct" and premium != 0:
        return premium
    part_b = values["part_b"] if values["premium_source"] == "medicare" else 0.0
    return (0.0 if values["premium_source"] == "direct" else premium) + part_b


def _situation(units, year, mode, unit_inputs=None):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    expected_premium, increase, roles = [], [], []
    unit_index = 0
    for variant in VARIANTS:
        for i, unit in enumerate(units):
            tag = f"{variant}_{i}"
            members, couple = [], []
            unit_increase = 0.0
            for j, (role, values) in enumerate(_entries(unit)):
                name = f"{tag}_{role}_{j}"
                people[name] = _person_inputs(unit, role, values, mode, variant)
                members.append(name)
                expected_premium.append(
                    _expected_premium(unit, role, values, mode, variant)
                )
                roles.append(role)
                if role == "dependent":
                    groups["marital_units"][f"{tag}_single_{j}"] = {"members": [name]}
                else:
                    couple.append(name)
                    unit_increase += sum(_increases(unit, role, values, mode, "raised"))
            increase.append(unit_increase)
            groups["marital_units"][f"{tag}_couple"] = {"members": couple}
            tax_unit = {"members": members}
            if mode == "unit":
                tax_unit["self_employed_health_insurance_ald"] = {
                    year: unit["supplied_unit_deduction"]
                }
            # Supplied for every tax unit, so none falls back to 0.
            for name, values in (unit_inputs or {}).items():
                tax_unit[name] = {year: float(values[unit_index])}
            unit_index += 1
            groups["tax_units"][f"{tag}_tax_unit"] = tax_unit
            groups["households"][f"{tag}_household"] = {
                "members": members,
                # Keyed by year: a bare value is not applied to the run year.
                "state_code": {year: "MT"},
            }
    people = {
        name: {key: {year: value} for key, value in values.items()}
        for name, values in people.items()
    }
    return (
        {"people": people, **groups},
        np.array(expected_premium),
        np.array(increase),
        np.array(roles),
    )


PERSON_VARIABLES = [
    "other_medical_expenses",
    "long_term_health_insurance_premiums",
    "medical_expense_health_insurance_premiums",
    "self_employed_health_insurance_ald_person",
    "mt_eligible_medical_insurance_premiums",
    "mt_eligible_long_term_care_insurance_premiums",
    "mt_agi_indiv",
    "mt_medical_expense_deduction_joint",
    "mt_medical_expense_deduction_indiv",
]
UNIT_VARIABLES = [
    "mt_agi_joint",
    "self_employed_health_insurance_ald",
    "mt_premium_deduction_joint",
    "itemized_medical_expenses",
    "itemized_medical_expenses_applied_exclusion",
    "itemized_medical_expenses_excluded_premiums",
    "itemized_medical_expenses_long_term_care_premiums",
    "medical_expense_deduction",
]


def _run(units, year, mode, unit_inputs=None):
    situation, expected_premium, increase, roles = _situation(
        units, year, mode, unit_inputs
    )
    sim = Simulation(situation=situation)
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in PERSON_VARIABLES + UNIT_VARIABLES
    }
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    out["filing_status"] = sim.calculate("filing_status", year).decode_to_str()
    out["state_code"] = sim.calculate("state_code", year).decode_to_str()
    out["expected_premium"] = expected_premium
    out["increase"] = increase
    out["role"] = roles
    return out


def _unit_sum(run, values):
    return np.bincount(run["unit"], weights=values, minlength=len(run["mt_agi_joint"]))


def _check(units, year, mode):
    run = _run(units, year, mode)
    n = len(units)
    base, raised, no_pre_tax = (slice(k * n, (k + 1) * n) for k in range(3))
    role = run["role"]
    joint = run["mt_medical_expense_deduction_joint"]
    indiv = run["mt_medical_expense_deduction_indiv"]
    deduction = _unit_sum(run, joint)
    assert (run["state_code"] == "MT").all()
    assert (joint[role != "head"] == 0).all()

    if year == FEDERAL_YEAR:
        # 8. Federal treatment from 2024.
        np.testing.assert_allclose(
            deduction, run["medical_expense_deduction"], atol=TOLERANCE
        )
        assert (indiv == 0).all()
        return None

    premium = run["medical_expense_health_insurance_premiums"]
    long_term_care = run["long_term_health_insurance_premiums"]
    own_deduction = np.maximum(run["self_employed_health_insurance_ald_person"], 0)
    line_2 = run["mt_eligible_medical_insurance_premiums"]
    line_3 = run["mt_eligible_long_term_care_insurance_premiums"]
    other = run["other_medical_expenses"]
    filer = role != "dependent"

    # 2. Premium conservation against closed forms.
    np.testing.assert_allclose(premium, run["expected_premium"], atol=TOLERANCE)
    if mode == "person":
        supplied = np.array(
            [
                v["supplied_deduction"]
                for _ in VARIANTS
                for unit in units
                for _, v in _entries(unit)
            ]
        )
        np.testing.assert_allclose(own_deduction, supplied, atol=TOLERANCE)
    if mode == "unit":
        supplied_unit = np.array(
            [unit["supplied_unit_deduction"] for _ in VARIANTS for unit in units]
        )
        np.testing.assert_allclose(
            run["self_employed_health_insurance_ald"], supplied_unit, atol=TOLERANCE
        )
    np.testing.assert_allclose(
        line_2 + line_3,
        np.maximum(run["expected_premium"] + long_term_care - own_deduction, 0),
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        line_2,
        run["expected_premium"] - np.minimum(run["expected_premium"], own_deduction),
        atol=TOLERANCE,
    )
    assert (line_3 <= long_term_care + TOLERANCE).all()
    return_deduction = np.maximum(run["self_employed_health_insurance_ald"], 0)
    expected_joint_premiums = np.maximum(
        _unit_sum(run, filer * (run["expected_premium"] + long_term_care))
        - return_deduction,
        0,
    )
    full = run["mt_premium_deduction_joint"]
    np.testing.assert_allclose(full, expected_joint_premiums, atol=TOLERANCE)

    # 1. Accounting, joint and separate.
    floored = np.maximum(_unit_sum(run, other) - FORM_FLOOR * run["mt_agi_joint"], 0)
    np.testing.assert_allclose(deduction, floored + full, atol=TOLERANCE)
    expected_indiv = filer * (
        np.maximum(other - FORM_FLOOR * run["mt_agi_indiv"], 0) + line_2 + line_3
    )
    np.testing.assert_allclose(indiv, expected_indiv, atol=TOLERANCE)

    # 3. Bounds.
    assert (deduction >= full - TOLERANCE).all()
    assert (deduction <= full + _unit_sum(run, other) + TOLERANCE).all()

    # 4. Slope of one for filer increases no deduction can absorb, and zero
    # for dependent increases. The raised twin changes both sets of payers.
    np.testing.assert_allclose(
        run["mt_agi_joint"][raised], run["mt_agi_joint"][base], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        deduction[raised] - deduction[base],
        run["increase"][raised],
        atol=TOLERANCE,
    )

    # 5. Pre-tax premiums never reach lines 2 or 3.
    np.testing.assert_allclose(full[no_pre_tax], full[base], atol=TOLERANCE)
    np.testing.assert_allclose(
        _unit_sum(run, line_2 + line_3)[no_pre_tax],
        _unit_sum(run, line_2 + line_3)[base],
        atol=TOLERANCE,
    )

    # 6. Line 1 base tracks the federal definition apart from the premiums.
    # The generator never supplies the subtotal, so it holds no long-term care
    # premiums.
    assert (run["itemized_medical_expenses_long_term_care_premiums"] == 0).all()
    np.testing.assert_allclose(
        _unit_sum(run, other),
        run["itemized_medical_expenses"]
        + run["itemized_medical_expenses_applied_exclusion"]
        - _unit_sum(run, filer * premium)
        - run["itemized_medical_expenses_long_term_care_premiums"],
        atol=TOLERANCE,
    )

    # 7. Single filers with person-level deductions: both variants agree.
    if mode != "unit":
        single = run["filing_status"] == "SINGLE"
        np.testing.assert_allclose(
            deduction[single], _unit_sum(run, indiv)[single], atol=TOLERANCE
        )
    return run, floored, full


# A batch's cost is mostly the simulation build and per-variable overhead, so
# each example is a large batch and there are few examples.
SETTINGS = dict(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(
    st.sampled_from(YEARS),
    st.sampled_from(MODES),
    st.lists(tax_units(), min_size=5, max_size=20),
)
def test_mt_medical_premium_deduction_invariants(year, mode, units):
    _check(units, year, mode)


# Each state year takes the deduction a different way; 2024 checks the federal
# branch.
SEEDED_CASES = [(2021, "derived"), (2022, "person"), (2023, "unit"), (2024, "unit")]


@pytest.mark.parametrize("year,mode", SEEDED_CASES)
def test_seeded_population(year, mode):
    units = _seeded_units()
    result = _check(units, year, mode)
    if result is None:
        return
    run, floored, full = result
    # The slope check includes dependent-only increases: their premiums rise
    # while the filers' premiums and deduction remain unchanged.
    dependent_increase = np.array(
        [
            sum(
                sum(_increases(unit, role, values, mode, "raised"))
                for role, values in _entries(unit)
                if role == "dependent"
            )
            for unit in units
        ]
    )
    assert np.any((dependent_increase > 1) & (run["increase"][: len(units)] == 0))
    # Non-vacuity: some returns deduct premiums while line 1 is below the
    # floor, where flooring premiums with other expenses would cut the
    # deduction; some deduct line 1 too; there are single and joint returns;
    # and each mode's deduction reduces lines 2 and 3 somewhere.
    agi_floor = FORM_FLOOR * run["mt_agi_joint"]
    total = _unit_sum(
        run,
        run["other_medical_expenses"]
        + run["medical_expense_health_insurance_premiums"],
    )
    assert np.any((full > 0) & (total < agi_floor))
    assert np.any((full > 0) & (floored > 0))
    assert np.any(run["filing_status"] == "SINGLE")
    assert np.any(run["filing_status"] == "JOINT")
    deduction = run["self_employed_health_insurance_ald_person"]
    premiums = run["medical_expense_health_insurance_premiums"]
    long_term_care = run["long_term_health_insurance_premiums"]
    line_2 = run["mt_eligible_medical_insurance_premiums"]
    line_3 = run["mt_eligible_long_term_care_insurance_premiums"]
    if mode == "derived":
        # A deduction derived from self-employment income reduces line 2.
        assert np.any((deduction > 0) & (line_2 < premiums - 1))
    if mode == "person":
        # A deduction above the medical premiums reduces line 3.
        assert np.any((deduction > premiums) & (line_3 < long_term_care - 1))
    if mode == "unit":
        # A return-level deduction reduces the filers' lines 2 and 3.
        filer = run["role"] != "dependent"
        gross = _unit_sum(run, filer * (premiums + long_term_care))
        assert np.any(full < gross - 1)
    _check_net_subtotal(run, units, year, mode)


def _check_net_subtotal(run, units, year, mode):
    """9. A net Schedule A subtotal gives the computed path's deduction.

    Supply, for every return, the subtotal as Schedule A line 1 would hold it
    (the computed subtotal plus the filers' long-term care premiums the
    self-employed deduction did not take), the exclusion as all premiums that
    deduction took (medical first), and the long-term care premiums still
    inside. Montana's deduction must not change.
    """
    filer = run["role"] != "dependent"
    return_deduction = np.maximum(run["self_employed_health_insurance_ald"], 0)
    medical_excluded = run["itemized_medical_expenses_excluded_premiums"]
    filer_long_term_care = _unit_sum(
        run, filer * run["long_term_health_insurance_premiums"]
    )
    long_term_care_excluded = np.minimum(
        filer_long_term_care, return_deduction - medical_excluded
    )
    inside = filer_long_term_care - long_term_care_excluded
    net = _run(
        units,
        year,
        mode,
        {
            "itemized_medical_expenses": run["itemized_medical_expenses"] + inside,
            "itemized_medical_expenses_applied_exclusion": medical_excluded
            + long_term_care_excluded,
            "itemized_medical_expenses_long_term_care_premiums": inside,
        },
    )
    np.testing.assert_allclose(net["mt_agi_joint"], run["mt_agi_joint"], atol=TOLERANCE)
    np.testing.assert_allclose(
        _unit_sum(net, net["mt_medical_expense_deduction_joint"]),
        _unit_sum(run, run["mt_medical_expense_deduction_joint"]),
        atol=TOLERANCE,
    )
    # Non-vacuity: with supplied deductions, some exclusions cover long-term
    # care premiums on returns with dependents' premiums, where taking the
    # exclusion from every member's premiums would differ. A derived
    # deduction never exceeds the filers' own medical premiums.
    if mode != "derived":
        dependent_premiums = _unit_sum(
            run, ~filer * run["medical_expense_health_insurance_premiums"]
        )
        assert np.any((long_term_care_excluded > 1) & (dependent_premiums > 1))
