"""Repealing state dependent exemptions keeps each state's rule for a filer
who can be claimed as a dependent on another return.

The contributed reform `repeal_state_dependent_exemptions` overrides 21 state
formulas so that they count only the filers' own exemptions. Where a state's
baseline gives no personal exemption to a filer whom another taxpayer can
claim, the override keeps that rule; where the baseline lets such a filer keep
it (Georgia, Indiana, Iowa, Kansas from 2024, Kentucky and Massachusetts), so
does the override.

The YAML tests in tests/policy/contrib/state_dependent_exemptions check fixed
households. This module checks, across couples and single filers drawn by
Hypothesis and a seeded population in the 19 states, with either, both or
neither filer claimable (and, if so, claimed or not, with or without the
would-be claimant's filing exception), and in two years, the properties a
YAML case cannot express because it runs only one system:

1. Swap invariance: each output is the same under either head/spouse
   labelling of a couple.
2. Monotonicity: under the reform, marking another filer as claimable never
   raises an exemption.
3. Bound: the reform never raises an output above the baseline.
4. No dependents, no change: on a return without dependents the reform
   equals the baseline.
5. A claimable filer, no change: a return with a filer who can be claimed
   has no dependents (IRC 152(b)(1)) unless the would-be claimant meets the
   filing exception, so on such a return the reform equals the baseline.

Each property runs one baseline and one reform simulation over a vectorized
batch. The reform is built once and cached by policyengine-core.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.reforms.state_dependent_exemptions.repeal_state_dependent_exemptions import (
    repeal_state_dependent_exemptions,
)
from policyengine_us.tests.core.test_dependent_elsewhere_head_spouse_swap_invariance import (
    TOLERANCE,
    adults,
    dependents,
)

STATES = [
    "CA",
    "DE",
    "GA",
    "HI",
    "IA",
    "IN",
    "KS",
    "KY",
    "MA",
    "MD",
    "MI",
    "NE",
    "OH",
    "OK",
    "RI",
    "VA",
    "VT",
    "WI",
    "WV",
]
# Kansas switches from per-person to filing-status exemptions in 2024.
YEARS = [2023, 2026]
# The reform's outputs, each compared with the baseline variable named here:
# the reform overrides Delaware's applied personal credit with its amount
# before the tax-liability limit, which ordered_capped_state_non_refundable_
# credits applies afterwards, so it is compared with the baseline's potential.
TAX_UNIT_OUTPUTS = {
    "hi_regular_exemptions": "hi_regular_exemptions",
    "md_total_personal_exemptions": "md_total_personal_exemptions",
    "mi_personal_exemptions": "mi_personal_exemptions",
    "mi_exemptions": "mi_exemptions",
    "ne_exemptions": "ne_exemptions",
    "oh_personal_exemptions": "oh_personal_exemptions",
    "ok_count_exemptions": "ok_count_exemptions",
    "ri_exemptions": "ri_exemptions",
    "vt_personal_exemptions": "vt_personal_exemptions",
    "va_personal_exemption": "va_personal_exemption",
    "wv_personal_exemption": "wv_personal_exemption",
    "ca_exemptions": "ca_exemptions",
    "ga_exemptions": "ga_exemptions",
    "in_base_exemptions": "in_base_exemptions",
    "ia_exemption_credit": "ia_exemption_credit",
    "ks_exemptions": "ks_exemptions",
    "ma_income_tax_exemption_threshold": "ma_income_tax_exemption_threshold",
    "wi_base_exemption": "wi_base_exemption",
    "de_personal_credit": "de_personal_credit_potential",
    "ky_family_size_tax_credit_threshold": "ky_family_size_tax_credit_threshold",
    "ok_child_care_child_tax_credit": "ok_child_care_child_tax_credit",
}
PERSON_OUTPUTS = {
    "oh_personal_exemptions_eligible_person": "oh_personal_exemptions_eligible_person",
    "va_personal_exemption_person": "va_personal_exemption_person",
}
# Oklahoma's credit is a share of the federal child care credit allowed after
# the federal tax-liability limit, which can rise when a claimable filer's
# smaller standard deduction raises federal tax; it is not an exemption.
NOT_MONOTONE = {"ok_child_care_child_tax_credit"}
# Outputs whose baseline still counts the dependents on a return with a
# claimable filer, so property 5 does not apply: Kentucky's family size is
# the tax unit size, and Michigan's baseline does not read
# mi_personal_exemptions on such a return (mi_exemptions is checked instead).
COUNTS_DEPENDENTS_OF_CLAIMABLE_FILER = {
    "ky_family_size_tax_credit_threshold",
    "mi_personal_exemptions",
}


@st.composite
def claim_facts(draw):
    # Claimed implies claimable; the exception matters only when claimable.
    claimable = draw(st.booleans())
    return {
        "claimable": claimable,
        "claimed": claimable and draw(st.booleans()),
        "exception": draw(st.booleans()),
    }


@st.composite
def units(draw):
    n_adults = draw(st.sampled_from([1, 2]))
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()) for _ in range(n_adults)],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claims": [draw(claim_facts()) for _ in range(n_adults)],
    }


SEED = 20261010


def _seeded_units():
    rng = np.random.default_rng(SEED)
    out = []
    for state in STATES:
        for n_adults in (1, 2, 2):
            claimable = rng.permutation([True] + [False] * (n_adults - 1))
            out.append(
                {
                    "state": state,
                    "adults": [
                        {
                            "age": int(rng.choice([19, 20, 40, 70])),
                            "employment_income": float(
                                rng.choice([0, 8_000, 40_000, 120_000])
                            ),
                            "is_blind": bool(rng.random() < 0.1),
                        }
                        for _ in range(n_adults)
                    ],
                    "dependents": [
                        {"age": int(rng.integers(0, 18))}
                        for _ in range(int(rng.choice([0, 1, 2])))
                    ],
                    "claims": [
                        {
                            "claimable": bool(c),
                            "claimed": bool(c) and bool(rng.random() < 0.7),
                            "exception": bool(rng.random() < 0.3),
                        }
                        for c in claimable
                    ],
                }
            )
    return out


def _situation(units, year, variants):
    """One copy of each unit per variant (first adult is head, claimable)."""
    people = {}
    groups = {
        "tax_units": {},
        "spm_units": {},
        "families": {},
        "marital_units": {},
        "households": {},
    }
    for i, unit in enumerate(units):
        couple = len(unit["adults"]) == 2
        for copy, (first_is_head, claimable) in enumerate(variants(unit)):
            names = []
            for slot, amounts in enumerate(unit["adults"]):
                name = f"adult_{i}_{copy}_{slot}"
                is_head = first_is_head if slot == 0 else not first_is_head
                facts = unit["claims"][slot]
                people[name] = {
                    **amounts,
                    "is_tax_unit_head": is_head,
                    "is_tax_unit_spouse": couple and not is_head,
                    "is_tax_unit_dependent": False,
                    "claimable_as_dependent_on_another_return": claimable[slot],
                    "claimed_as_dependent_on_another_return": claimable[slot]
                    and facts["claimed"],
                    "dependent_claimant_filing_exception": facts["exception"],
                }
                names.append(name)
            groups["marital_units"][f"adults_{i}_{copy}"] = {"members": list(names)}
            members = list(names)
            for j, amounts in enumerate(unit["dependents"]):
                child = f"dependent_{i}_{copy}_{j}"
                people[child] = {
                    **amounts,
                    "is_tax_unit_head": False,
                    "is_tax_unit_spouse": False,
                    "is_tax_unit_dependent": True,
                }
                members.append(child)
                groups["marital_units"][f"single_{i}_{copy}_{j}"] = {"members": [child]}
            for group, prefix in (
                ("tax_units", "tax_unit"),
                ("spm_units", "spm_unit"),
                ("families", "family"),
            ):
                groups[group][f"{prefix}_{i}_{copy}"] = {"members": members}
            groups["households"][f"household_{i}_{copy}"] = {
                "members": members,
                "state_code": {year: unit["state"]},
            }
    people = {
        name: {k: {year: v} for k, v in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _claimable(unit):
    return tuple(facts["claimable"] for facts in unit["claims"])


def _as_drawn(unit):
    return [(True, _claimable(unit))]


def _swap_variants(unit):
    # Singles have no labels to exchange, so both copies are the same.
    return [(True, _claimable(unit)), (len(unit["adults"]) == 1, _claimable(unit))]


def _monotone_variants(unit):
    # Nobody, either adult, then every adult claimable; labels fixed.
    if len(unit["adults"]) == 1:
        return [(True, (False,)), (True, (True,)), (True, (True,)), (True, (True,))]
    return [
        (True, (False, False)),
        (True, (True, False)),
        (True, (False, True)),
        (True, (True, True)),
    ]


def _simulations(units, year, variants):
    situation = _situation(units, year, variants)
    baseline = Simulation(situation=situation)
    # The module-level reform applies whatever the in_effect parameter says.
    reformed = Simulation(situation=situation, reform=repeal_state_dependent_exemptions)
    return baseline, reformed


def _values(sim, name, year):
    return np.asarray(sim.calculate(name, year), dtype=float)


def _person_index(units, variants):
    """Copy number and unit number of each person, in simulation order."""
    copies, owners = [], []
    for i, unit in enumerate(units):
        for copy, _ in enumerate(variants(unit)):
            n = len(unit["adults"]) + len(unit["dependents"])
            copies += [copy] * n
            owners += [i] * n
    return np.array(copies), np.array(owners)


def _describe(units, rows, a, b):
    return ", ".join(
        f"{units[i]['state']} claims={units[i]['claims']} "
        f"dependents={len(units[i]['dependents'])}: {a[k]:.2f} vs {b[k]:.2f}"
        for k, i in enumerate(rows[:10])
    )


def check_swap(units, year):
    """1. Each output is the same under either head/spouse labelling."""
    _, reformed = _simulations(units, year, _swap_variants)
    copies, _ = _person_index(units, _swap_variants)
    for name in TAX_UNIT_OUTPUTS:
        values = _values(reformed, name, year)
        drawn, swapped = values[0::2], values[1::2]
        differs = np.flatnonzero(~(np.abs(swapped - drawn) <= TOLERANCE))
        assert not differs.size, (
            f"{name} in {year} changes when the head and spouse labels are "
            "exchanged under the reform: "
            + _describe(units, differs, drawn[differs], swapped[differs])
        )
    for name in PERSON_OUTPUTS:
        values = _values(reformed, name, year)
        drawn, swapped = values[copies == 0], values[copies == 1]
        assert np.array_equal(drawn, swapped), (
            f"{name} in {year} changes for some person when the head and "
            "spouse labels are exchanged under the reform"
        )


def check_monotone(units, year):
    """2. Marking another filer as claimable never raises an exemption."""
    _, reformed = _simulations(units, year, _monotone_variants)
    for name in TAX_UNIT_OUTPUTS:
        if name in NOT_MONOTONE:
            continue
        values = _values(reformed, name, year).reshape(-1, 4)
        nobody, first, second, both = values.T
        for more, fewer, label in (
            (first, nobody, "first adult"),
            (second, nobody, "second adult"),
            (both, first, "every adult after the first"),
            (both, second, "every adult after the second"),
        ):
            rises = np.flatnonzero(more > fewer + TOLERANCE)
            assert not rises.size, (
                f"{name} in {year} rises under the reform when the {label} "
                "can be claimed elsewhere: "
                + _describe(units, rises, fewer[rises], more[rises])
            )


def check_against_baseline(units, year):
    """3-5. The reform against the baseline, return by return."""
    baseline, reformed = _simulations(units, year, _as_drawn)
    no_dependents = np.array([not u["dependents"] for u in units])
    # The baseline's own flag: a filer can be claimed and the would-be
    # claimant does not meet the filing exception.
    claimable_filer = (
        _values(
            baseline,
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception",
            year,
        )
        > 0
    )
    _, owners = _person_index(units, _as_drawn)
    checked = {3: 0, 4: 0, 5: 0}
    for outputs, mask_of in (
        (TAX_UNIT_OUTPUTS, lambda m: m),
        (PERSON_OUTPUTS, lambda m: m[owners]),
    ):
        for name, baseline_name in outputs.items():
            reform = _values(reformed, name, year)
            base = _values(baseline, baseline_name, year)
            rises = np.flatnonzero(reform > base + TOLERANCE)
            assert not rises.size, (
                f"{name} in {year} is higher under the reform than "
                f"{baseline_name} in the baseline: {reform[rises][:5]} vs "
                f"{base[rises][:5]}"
            )
            checked[3] += reform.size
            same = mask_of(no_dependents)
            checked[4] += int(same.sum())
            if name not in COUNTS_DEPENDENTS_OF_CLAIMABLE_FILER:
                with_rule = mask_of(claimable_filer)
                checked[5] += int((with_rule & ~same).sum())
                same = same | with_rule
            differs = np.flatnonzero(same & ~(np.abs(reform - base) <= TOLERANCE))
            assert not differs.size, (
                f"{name} in {year} differs from {baseline_name} in the "
                "baseline on a return the repeal should leave alone: "
                f"{reform[differs][:5]} vs {base[differs][:5]}"
            )
    return checked


@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.sampled_from(YEARS), st.lists(units(), min_size=10, max_size=20))
def test_repeal_keeps_claimable_filer_rules(year, drawn):
    check_swap(drawn, year)
    check_against_baseline(drawn, year)


@pytest.mark.parametrize("year", YEARS)
def test_repeal_keeps_claimable_filer_rules_seeded_population(year):
    seeded = _seeded_units()
    check_swap(seeded, year)
    check_monotone(seeded, year)
    checked = check_against_baseline(seeded, year)
    # The seeded population exercises every property: returns without
    # dependents, and returns with dependents and a claimable filer.
    assert all(checked.values()), checked
