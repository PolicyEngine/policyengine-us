"""SSI earned-source invariants and a differential against a reverted source list.

The three profit inputs represent disjoint active businesses. SSI counts their
signed sum alike: moving profit between Schedule C, Schedule F and a partner's
SECA earnings must not change earned income, and more profit must not raise SSI.

The reference reform freezes the earned-source list at main commit
8b17892d2cba99a82961ea32fbaf9d69c6ba73d6. With
farm and partnership earnings zero and the remaining business incomes
nonnegative, all SSI, MSP and direct state-reader outputs must remain exactly
equal to this list-reversion reference. Both policies retain this patch's
formula corrections: spouse-loss netting and nonnegative child-allocation and
student-exclusion income. The nonnegative domain excludes these corrections
and New Hampshire's distinct prohibition on offsetting wages with a business
loss; YAML covers those intentional changes. An actual git-base differential
is run separately. A seeded, stratified sample of 200 households supplements
the smaller Hypothesis batches, including spouses and disabled children.

All households in a batch share one vectorized simulation. The module reuses
the read-only country singleton and constructs its parameter-only reference
reform once, avoiding a country model for every example or household.
"""

from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.system import system


YEAR = 2026
MONTH = "2026-01"
MAIN_EARNED_SOURCES = (
    "employment_income",
    "self_employment_income",
    "sstb_self_employment_income",
)
PROFIT_SOURCES = (
    "self_employment_income",
    "farm_operations_income",
    "partnership_self_employment_net_earnings",
)
STATES = (
    "TX",
    "CA",
    "CO",
    "CT",
    "MN",
    "NC",
    "NH",
    "OH",
    "OK",
    "OR",
    "SD",
    "VA",
    "VT",
    "WI",
)
KINDS = ("single", "couple", "ineligible_spouse", "one_parent", "two_parents")
STATE_READERS = (
    "ca_wdp_gross_earned_income",
    "co_state_supplement_countable_income",
    "co_oap_own_countable_income",
    "co_oap_deemed_income",
    "ct_ssp_countable_income",
    "ct_ssp_earned_income_disregard",
    "ct_ssp_gross_income",
    "mn_msa_net_income_eligible",
    "mn_msa_gross_income",
    "mn_msa_person",
    "nc_sa_countable_income",
    "nh_ssp_countable_income",
    "oh_rss_countable_income",
    "ok_ssp_spouse_child_allocation",
    "or_ssp_countable_income",
    "sd_ssp_care",
    "va_ag_countable_income",
    "vt_aabd_ep_countable_income",
    "wi_cts_gross_earned_income",
)
OTHER_READERS = (
    "medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse",
    "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent",
    "medicare_part_b_premium",
)


class RevertAddedEarnedSources(Reform):
    """Revert only the two added sources, retaining current variable formulas."""

    def apply(self):
        self.parameters.gov.ssa.ssi.income.sources.earned.update(
            start="1975-01-01", value=list(MAIN_EARNED_SOURCES)
        )


@pytest.fixture(scope="module")
def policy():
    return system


@pytest.fixture(scope="module")
def policies(policy):
    return policy, RevertAddedEarnedSources(policy)


def _program_outputs(policy):
    """Include every variable defined within SSI/MSP, plus direct readers."""
    variables = Path(__file__).resolve().parents[2] / "variables"
    names = set(STATE_READERS + OTHER_READERS)
    for directory in (
        variables / "gov/ssa/ssi",
        variables / "gov/hhs/medicare/savings_programs",
    ):
        names.update(
            path.stem
            for path in directory.rglob("*.py")
            if not path.name.startswith("_")
        )
    # A renamed or removed reader must fail instead of silently shrinking
    # the differential's coverage.
    assert names <= policy.variables.keys()
    return sorted(names)


def _period(policy, name):
    return MONTH if policy.variables[name].definition_period == "month" else YEAR


def _person(age=67, **inputs):
    return {
        "age": age,
        "employment_income": 0,
        "self_employment_income": 0,
        "sstb_self_employment_income": 0,
        "farm_operations_income": 0,
        "partnership_self_employment_net_earnings": 0,
        "bank_account_assets": 0,
        "takes_up_ssi_if_eligible": True,
        **inputs,
    }


def _situation(households):
    situation = {
        name: {}
        for name in (
            "people",
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
            "households",
        )
    }
    for i, household in enumerate(households):
        adults = household["adults"]
        children = household.get("children", [])
        members = []
        for j, values in enumerate(adults + children):
            member = f"p{i}_{j}"
            child = j >= len(adults)
            inputs = {
                **values,
                "is_tax_unit_head": j == 0,
                "is_tax_unit_spouse": j == 1 and not child,
                "is_tax_unit_dependent": child,
                "is_household_head": j == 0,
                "is_parent": bool(children) and not child,
            }
            situation["people"][member] = {
                name: {YEAR: value} for name, value in inputs.items()
            }
            members.append(member)
        situation["marital_units"][f"adults_{i}"] = {"members": members[: len(adults)]}
        for child in members[len(adults) :]:
            situation["marital_units"][child] = {"members": [child]}
        for group in ("tax_units", "spm_units", "families"):
            situation[group][f"{group}_{i}"] = {"members": members}
        situation["households"][f"h{i}"] = {
            "members": members,
            "state_code": {YEAR: household["state"]},
        }
    return situation


def _simulation(policy, households):
    return Simulation(
        tax_benefit_system=policy,
        situation=_situation(households),
        default_input_period=YEAR,
    )


def _assert_main_equal(policies, households, outputs=None):
    situation = _situation(households)
    names = _program_outputs(policies[0]) if outputs is None else outputs
    snapshots = []
    # Release each simulation before creating the next one. Only the small
    # copied output arrays remain alive, reducing differential-test memory.
    for policy in policies:
        simulation = Simulation(
            tax_benefit_system=policy,
            situation=deepcopy(situation),
            default_input_period=YEAR,
        )
        snapshots.append(
            {
                name: simulation.calculate(name, _period(policy, name)).copy()
                for name in names
            }
        )
        del simulation
    for name in names:
        np.testing.assert_array_equal(
            snapshots[0][name], snapshots[1][name], err_msg=name
        )


@st.composite
def profit_partitions(draw):
    total = draw(st.integers(0, 80_000))
    farm = draw(st.integers(0, total))
    partnership = draw(st.integers(0, total - farm))
    return (
        draw(st.integers(0, 50_000)),
        draw(st.integers(0, 10_000)),
        total,
        farm,
        partnership,
    )


@settings(max_examples=12, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@example(batch=[(12_000, 0, 6_000, 2_000, 3_000), (0, 500, 1, 1, 0)])
@given(batch=st.lists(profit_partitions(), min_size=1, max_size=6))
def test_profit_repartition_preserves_ssi_earned_income(policy, batch):
    households = []
    expected = []
    for wages, sstb, total, farm, partnership in batch:
        splits = (
            (total, 0, 0),
            (0, total, 0),
            (0, 0, total),
            (total - farm - partnership, farm, partnership),
        )
        for split in splits:
            households.append(
                {
                    "state": "TX",
                    "adults": [
                        _person(
                            employment_income=wages,
                            sstb_self_employment_income=sstb,
                            **dict(zip(PROFIT_SOURCES, split)),
                        )
                    ],
                }
            )
            expected.append(wages + sstb + total)
    simulation = _simulation(policy, households)
    earned = simulation.calculate("ssi_earned_income", YEAR)
    np.testing.assert_array_equal(earned, expected)
    np.testing.assert_array_equal(
        earned.reshape(-1, 4), np.repeat(earned.reshape(-1, 4)[:, :1], 4, axis=1)
    )


@settings(max_examples=12, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@example(batch=[(0, 0, 60_000, "farm_operations_income", False)])
@given(
    batch=st.lists(
        st.tuples(
            st.integers(0, 30_000),
            st.integers(0, 40_000),
            st.integers(0, 40_000),
            st.sampled_from(PROFIT_SOURCES),
            st.booleans(),
        ),
        min_size=1,
        max_size=6,
    )
)
def test_ssi_never_rises_when_business_profit_rises(policy, batch):
    households = []
    for wages, initial, increase, source, married in batch:
        for profit in (initial, initial + increase):
            adults = [_person(employment_income=wages, **{source: profit})]
            if married:
                adults.append(_person(age=45))
            households.append({"state": "TX", "adults": adults})
    simulation = _simulation(policy, households)
    # Sum within each household so the married case includes any payment
    # attributed to a spouse as well as the applicant's own payment.
    amounts = simulation.populations["household"].sum(
        simulation.calculate("ssi", MONTH)
    )
    pairs = np.asarray(amounts).reshape(-1, 2)
    assert np.all(pairs[:, 1] <= pairs[:, 0])


@st.composite
def people_without_farm_or_partnership(draw, age):
    wages = draw(st.integers(0, 40_000))
    disabled = draw(st.booleans())
    return _person(
        age=age,
        employment_income=wages,
        self_employment_income=draw(st.integers(0, 30_000)),
        sstb_self_employment_income=draw(st.integers(0, 10_000)),
        pre_tax_health_insurance_premiums=draw(st.integers(0, min(wages, 6_000))),
        social_security_retirement=draw(st.integers(0, 20_000)) if age >= 62 else 0,
        taxable_interest_income=draw(st.integers(0, 1_200)),
        bank_account_assets=draw(st.sampled_from((0, 500, 1_999, 2_001, 4_000))),
        is_disabled=disabled,
        meets_ssi_disability_criteria=disabled,
        is_blind=draw(st.booleans()),
    )


@st.composite
def households_without_farm_or_partnership(draw):
    kind = draw(st.sampled_from(KINDS))
    parental = kind in ("one_parent", "two_parents")
    age = draw(st.integers(30, 55) if parental else st.integers(65, 85))
    adults = [draw(people_without_farm_or_partnership(age))]
    if kind in ("couple", "ineligible_spouse", "two_parents"):
        spouse_age = 45 if kind == "ineligible_spouse" else age
        adults.append(draw(people_without_farm_or_partnership(spouse_age)))
    children = []
    if parental:
        child_age = draw(st.integers(6, 17))
        children = [
            _person(
                age=child_age,
                is_disabled=True,
                meets_ssi_disability_criteria=True,
                employment_income=draw(st.integers(0, 2_000)),
            )
        ]
    return {
        "state": draw(st.sampled_from(STATES)),
        "adults": adults,
        "children": children,
    }


@settings(max_examples=6, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    households=st.lists(
        households_without_farm_or_partnership(),
        min_size=1,
        max_size=5,
    )
)
def test_zero_farm_and_partnership_preserves_list_reference_on_nonnegative_domain(
    policies, households
):
    _assert_main_equal(policies, households)


def _seeded_households():
    rng = np.random.default_rng(20261029)

    def person(age):
        wages = int(rng.integers(0, 40_001)) if rng.random() < 0.75 else 0
        disabled = bool(rng.random() < 0.35)
        return _person(
            age=age,
            employment_income=wages,
            self_employment_income=int(rng.integers(0, 30_001))
            if rng.random() < 0.65
            else 0,
            sstb_self_employment_income=int(rng.integers(0, 10_001))
            if rng.random() < 0.25
            else 0,
            pre_tax_health_insurance_premiums=int(
                rng.integers(0, min(wages, 6_000) + 1)
            ),
            social_security_retirement=int(rng.integers(0, 20_001))
            if age >= 62 and rng.random() < 0.7
            else 0,
            taxable_interest_income=int(rng.integers(0, 1_201)),
            bank_account_assets=int(rng.choice((0, 500, 1_999, 2_001, 4_000))),
            is_disabled=disabled,
            meets_ssi_disability_criteria=disabled,
            is_blind=bool(rng.random() < 0.15),
        )

    households = []
    for i in range(200):
        kind = KINDS[(i // len(STATES)) % len(KINDS)]
        parental = kind in ("one_parent", "two_parents")
        age = int(rng.integers(30, 56) if parental else rng.integers(65, 86))
        adults = [person(age)]
        if kind in ("couple", "ineligible_spouse", "two_parents"):
            adults.append(person(45 if kind == "ineligible_spouse" else age))
        children = []
        if parental:
            children = [
                _person(
                    age=int(rng.integers(6, 18)),
                    is_disabled=True,
                    meets_ssi_disability_criteria=True,
                    employment_income=int(rng.integers(0, 2_001)),
                )
            ]
        households.append(
            {
                "state": STATES[i % len(STATES)],
                "adults": adults,
                "children": children,
            }
        )
    return households


def test_200_households_match_reverted_list_without_farm_or_partnership(policies):
    households = _seeded_households()
    assert len(households) == 200
    assert {household["state"] for household in households} == set(STATES)
    _assert_main_equal(policies, households)
