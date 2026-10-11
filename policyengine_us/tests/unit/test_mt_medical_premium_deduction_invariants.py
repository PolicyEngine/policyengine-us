"""Invariants for Montana's 2021-2023 medical insurance premium deduction.

The 2021-2023 Form 2 Itemized Deductions Schedule floors only line 1, medical
and dental expenses other than insurance premiums, at 7.5% of Montana AGI.
Line 2 deducts medical insurance premiums in full and line 3 long-term care
insurance premiums in full, except premiums already deducted in Montana AGI
through the self-employed health insurance deduction, and pre-tax premiums.
Former MCA 15-30-2131(1)(a)(iii)-(iv) and (1)(g). From 2024 Montana takes
federal itemized deductions, where premiums stay under the federal floor.

Why Python rather than YAML: Hypothesis generates mixed populations (single,
head of household and joint returns with dependents; premiums reported
directly, decomposed or with Medicare Part B; derived and supplied
self-employed deductions), and every batch also holds twins of each return
whose differences are asserted. YAML cases check fixed examples; these
properties check relations between generated returns.

Each batch runs as one vectorized simulation holding three copies of every
tax unit: the drawn return, a twin with higher after-tax and long-term care
premiums for people with no self-employed deduction, and a twin with no
pre-tax premiums. The 7.5% rate is taken from Form 2 line 1c rather than the
model's parameters. Montana AGI and the self-employed deduction are read from
the model; they are inputs to these properties, not derived independently.
For every tax unit:

1. Accounting (2021-2023): the joint deduction is
   max(0, other expenses - 7.5% x Montana AGI) + line 2 + line 3, held by the
   head. The separate variant is the same per head and spouse on their own
   Montana AGI; dependents hold nothing.
2. Premium conservation, per person, against a closed form: line 2 + line 3
   = max(0, premiums + long-term care premiums - self-employed deduction),
   with premiums computed from the raw inputs. Line 2 alone is the premiums
   less the part of the deduction they absorb. So the deduction is netted
   exactly once.
3. Bounds (2021-2023): premiums are never floored, so the deduction is at
   least lines 2 and 3 and at most those plus other expenses.
4. Slope (2021-2023): raising after-tax premiums or long-term care premiums
   of people with no self-employed deduction raises the deduction by exactly
   the increase. Montana AGI is unchanged by those increases (asserted).
5. Pre-tax premiums never change lines 2 or 3.
6. Line 1 base: other expenses equal federal itemized medical expenses plus
   the self-employed premiums those exclude, less the premiums. Line 1
   therefore tracks the federal definition apart from the premiums.
7. Differential (2021-2023): for single filers the joint and separate
   variants agree.
8. From 2024 the joint deduction is the federal medical expense deduction and
   the separate variant is zero.
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
VARIANTS = ["base", "raised", "no_pre_tax"]

amount = st.one_of(st.just(0.0), st.integers(1, 15_000).map(float))
small_amount = st.one_of(st.just(0.0), st.integers(1, 5_000).map(float))


@st.composite
def people(draw):
    self_employed = draw(st.booleans())
    return {
        "employment_income": float(draw(st.integers(0, 150_000))),
        "self_employed": self_employed,
        "self_employment_income": (
            float(draw(st.integers(-20_000, 60_000))) if self_employed else 0.0
        ),
        # A deduction claimed on Schedule 1, line 17, supplied as an input.
        "supplied_deduction": draw(
            st.one_of(st.none(), st.integers(0, 20_000).map(float))
        ),
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
            "supplied_deduction": (
                float(rng.integers(0, 20_001)) if rng.random() < 0.2 else None
            ),
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
            }
        )
    return units


def _may_have_deduction(values):
    return values["self_employed"] or values["supplied_deduction"] is not None


def _increases(values, variant):
    """Premium increases for the raised twin, for people with no deduction."""
    if variant != "raised" or _may_have_deduction(values):
        return 0.0, 0.0
    return values["premium_increase"], values["long_term_care_increase"]


def _person_inputs(values, role, variant):
    premium_increase, long_term_care_increase = _increases(values, variant)
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
    if values["supplied_deduction"] is not None:
        inputs["self_employed_health_insurance_ald_person"] = values[
            "supplied_deduction"
        ]
    return inputs


def _expected_premium(values, variant):
    """Premiums counted as federal medical expenses, from the inputs alone."""
    premium = values["premium"] + _increases(values, variant)[0]
    if values["premium_source"] == "direct" and premium != 0:
        return premium
    part_b = values["part_b"] if values["premium_source"] == "medicare" else 0.0
    return (0.0 if values["premium_source"] == "direct" else premium) + part_b


def _situation(units, year):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    expected_premium, increase, roles, supplied = [], [], [], []
    for variant in VARIANTS:
        for i, unit in enumerate(units):
            tag = f"{variant}_{i}"
            members, couple = [], []
            entries = [("head", unit["head"])]
            if unit["spouse"] is not None:
                entries.append(("spouse", unit["spouse"]))
            entries += [("dependent", d) for d in unit["dependents"]]
            unit_increase = 0.0
            for j, (role, values) in enumerate(entries):
                name = f"{tag}_{role}_{j}"
                people[name] = _person_inputs(values, role, variant)
                members.append(name)
                expected_premium.append(_expected_premium(values, variant))
                roles.append(role)
                supplied.append(
                    np.nan
                    if values["supplied_deduction"] is None
                    else values["supplied_deduction"]
                )
                if role == "dependent":
                    groups["marital_units"][f"{tag}_single_{j}"] = {"members": [name]}
                else:
                    couple.append(name)
                unit_increase += sum(_increases(values, "raised"))
            increase.append(unit_increase)
            groups["marital_units"][f"{tag}_couple"] = {"members": couple}
            groups["tax_units"][f"{tag}_tax_unit"] = {"members": members}
            groups["households"][f"{tag}_household"] = {
                "members": members,
                "state_code": "MT",
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
        np.array(supplied),
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
    "itemized_medical_expenses",
    "itemized_medical_expenses_applied_exclusion",
    "medical_expense_deduction",
]


def _run(units, year):
    situation, expected_premium, increase, roles, supplied = _situation(units, year)
    sim = Simulation(situation=situation)
    out = {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in PERSON_VARIABLES + UNIT_VARIABLES
    }
    out["unit"] = sim.populations["tax_unit"].members_entity_id
    out["filing_status"] = sim.calculate("filing_status", year).decode_to_str()
    out["expected_premium"] = expected_premium
    out["increase"] = increase
    out["role"] = roles
    out["supplied"] = supplied
    return out


def _unit_sum(run, values):
    return np.bincount(run["unit"], weights=values, minlength=len(run["mt_agi_joint"]))


def _check(units, year):
    run = _run(units, year)
    n = len(units)
    base, raised, no_pre_tax = (slice(k * n, (k + 1) * n) for k in range(3))
    role = run["role"]
    joint = run["mt_medical_expense_deduction_joint"]
    indiv = run["mt_medical_expense_deduction_indiv"]
    deduction = _unit_sum(run, joint)
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
    se_deduction = np.maximum(run["self_employed_health_insurance_ald_person"], 0)
    line_2 = run["mt_eligible_medical_insurance_premiums"]
    line_3 = run["mt_eligible_long_term_care_insurance_premiums"]
    other = run["other_medical_expenses"]

    # 2. Premium conservation against a closed form.
    np.testing.assert_allclose(premium, run["expected_premium"], atol=TOLERANCE)
    supplied = ~np.isnan(run["supplied"])
    np.testing.assert_allclose(
        se_deduction[supplied], run["supplied"][supplied], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        line_2 + line_3,
        np.maximum(run["expected_premium"] + long_term_care - se_deduction, 0),
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        line_2,
        run["expected_premium"] - np.minimum(run["expected_premium"], se_deduction),
        atol=TOLERANCE,
    )
    assert (line_3 <= long_term_care + TOLERANCE).all()

    # 1. Accounting, joint and separate.
    full = _unit_sum(run, line_2 + line_3)
    floored = np.maximum(_unit_sum(run, other) - FORM_FLOOR * run["mt_agi_joint"], 0)
    np.testing.assert_allclose(deduction, floored + full, atol=TOLERANCE)
    filer = role != "dependent"
    expected_indiv = filer * (
        np.maximum(other - FORM_FLOOR * run["mt_agi_indiv"], 0) + line_2 + line_3
    )
    np.testing.assert_allclose(indiv, expected_indiv, atol=TOLERANCE)

    # 3. Bounds.
    assert (deduction >= full - TOLERANCE).all()
    assert (deduction <= full + _unit_sum(run, other) + TOLERANCE).all()

    # 4. Slope of one for people with no self-employed deduction.
    np.testing.assert_allclose(
        run["mt_agi_joint"][raised], run["mt_agi_joint"][base], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        deduction[raised] - deduction[base],
        run["increase"][raised],
        atol=TOLERANCE,
    )

    # 5. Pre-tax premiums never reach lines 2 or 3.
    np.testing.assert_allclose(
        _unit_sum(run, line_2 + line_3)[no_pre_tax],
        _unit_sum(run, line_2 + line_3)[base],
        atol=TOLERANCE,
    )

    # 6. Line 1 base tracks the federal definition apart from the premiums.
    np.testing.assert_allclose(
        _unit_sum(run, other),
        run["itemized_medical_expenses"]
        + run["itemized_medical_expenses_applied_exclusion"]
        - _unit_sum(run, premium),
        atol=TOLERANCE,
    )

    # 7. Single filers: joint and separate variants agree.
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
@given(st.sampled_from(YEARS), st.lists(tax_units(), min_size=5, max_size=20))
def test_mt_medical_premium_deduction_invariants(year, units):
    _check(units, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    result = _check(_seeded_units(), year)
    if result is None:
        return
    run, floored, full = result
    # Non-vacuity: some returns deduct premiums while line 1 is below the
    # floor, where flooring premiums with other expenses would cut the
    # deduction; some deduct line 1 too; some people have a self-employed
    # deduction larger than their medical premiums that reduces line 3; and
    # there are single and joint returns.
    agi_floor = FORM_FLOOR * run["mt_agi_joint"]
    total = _unit_sum(
        run,
        run["other_medical_expenses"]
        + run["medical_expense_health_insurance_premiums"],
    )
    assert np.any((full > 0) & (total < agi_floor))
    assert np.any((full > 0) & (floored > 0))
    deduction = run["self_employed_health_insurance_ald_person"]
    long_term_care = run["long_term_health_insurance_premiums"]
    line_3 = run["mt_eligible_long_term_care_insurance_premiums"]
    assert np.any(
        (deduction > run["medical_expense_health_insurance_premiums"])
        & (line_3 < long_term_care - 1)
    )
    assert np.any(run["filing_status"] == "SINGLE")
    assert np.any(run["filing_status"] == "JOINT")
