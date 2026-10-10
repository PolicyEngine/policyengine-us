"""Repealing state dependent exemptions keeps each state's rule for a filer
who can be claimed as a dependent on another return.

The contributed reform `repeal_state_dependent_exemptions` overrides 20 state
formulas so that they count only the filers' own exemptions. Where a state's
baseline gives no personal exemption (in Oklahoma, no regular exemption) to
a filer whom another taxpayer can claim (Delaware, Hawaii, Michigan, Ohio,
Oklahoma, Rhode Island, Vermont, Virginia, West Virginia and Wisconsin), the
override keeps that rule; elsewhere the baseline counts every head and
spouse, and so does the override.

The YAML tests in tests/policy/contrib/state_dependent_exemptions check fixed
households. This module checks, across couples and single filers drawn by
Hypothesis and a seeded population in the 19 states, with either, both or
neither filer claimed, and in two years, the properties a YAML case cannot
express because it runs only one system:

1. Swap invariance: each output is the same under either head/spouse
   labelling of a couple.
2. Monotonicity: under the reform, marking another filer as claimed never
   raises an exemption.
3. Bound: the reform never raises an output above the baseline.
4. No dependents, no change: on a return without dependents the reform
   equals the baseline.
5. A claimable filer, no change: a return with a claimable filer has no
   dependents (IRC 152(b)(1)) in the states whose baseline applies that rule
   and the claimable filer's own rule, so there the reform equals the
   baseline.

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
# the federal tax-liability limit, which can rise when a claimed filer's
# smaller standard deduction raises federal tax; it is not an exemption.
NOT_MONOTONE = {"ok_child_care_child_tax_credit"}
# Outputs whose baseline gives a return with a claimable filer no dependents
# and that filer no personal exemption (in Oklahoma, no regular exemption;
# in West Virginia, $500 once per return when no filer has one).
CLAIM_RULE_OUTPUTS = {
    "de_personal_credit",
    "hi_regular_exemptions",
    "mi_exemptions",
    "oh_personal_exemptions",
    "oh_personal_exemptions_eligible_person",
    "ok_count_exemptions",
    "ri_exemptions",
    "va_personal_exemption",
    "va_personal_exemption_person",
    "vt_personal_exemptions",
    "wi_base_exemption",
    "wv_personal_exemption",
}


@st.composite
def units(draw):
    n_adults = draw(st.sampled_from([1, 2]))
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": [draw(adults()) for _ in range(n_adults)],
        "dependents": draw(st.lists(dependents(), max_size=2)),
        "claimed": tuple(draw(st.booleans()) for _ in range(n_adults)),
    }


SEED = 20261010


def _seeded_units():
    rng = np.random.default_rng(SEED)
    out = []
    for state in STATES:
        for n_adults in (1, 2, 2):
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
                    "claimed": tuple(
                        bool(c)
                        for c in rng.permutation([True] + [False] * (n_adults - 1))
                    ),
                }
            )
    return out


def _situation(units, year, variants):
    """One copy of each unit per variant (first adult is head, claims)."""
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
        for copy, (first_is_head, claims) in enumerate(variants(unit)):
            names = []
            for slot, (amounts, claimed) in enumerate(zip(unit["adults"], claims)):
                name = f"adult_{i}_{copy}_{slot}"
                is_head = first_is_head if slot == 0 else not first_is_head
                people[name] = {
                    **amounts,
                    "is_tax_unit_head": is_head,
                    "is_tax_unit_spouse": couple and not is_head,
                    "is_tax_unit_dependent": False,
                    "claimed_as_dependent_on_another_return": claimed,
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


def _as_drawn(unit):
    return [(True, unit["claimed"])]


def _swap_variants(unit):
    # Singles have no labels to exchange, so both copies are the same.
    return [(True, unit["claimed"]), (len(unit["adults"]) == 1, unit["claimed"])]


def _monotone_variants(unit):
    # Nobody, either adult, then every adult claimed; labels fixed.
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
        f"{units[i]['state']} adults={len(units[i]['adults'])} "
        f"claimed={units[i]['claimed']} "
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
    """2. Marking another filer as claimed never raises an exemption."""
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
                "is claimed elsewhere: "
                + _describe(units, rises, fewer[rises], more[rises])
            )


def check_against_baseline(units, year):
    """3-5. The reform against the baseline, return by return."""
    baseline, reformed = _simulations(units, year, _as_drawn)
    no_dependents = np.array([not u["dependents"] for u in units])
    claimable = np.array([any(u["claimed"]) for u in units])
    _, owners = _person_index(units, _as_drawn)
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
                f"{baseline_name} in the baseline"
            )
            same = mask_of(no_dependents)
            if name in CLAIM_RULE_OUTPUTS:
                same = same | mask_of(claimable)
            differs = np.flatnonzero(same & ~(np.abs(reform - base) <= TOLERANCE))
            assert not differs.size, (
                f"{name} in {year} differs from {baseline_name} in the "
                "baseline on a return the repeal should leave alone"
            )


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
    check_against_baseline(seeded, year)
