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
student-exclusion income. The nonnegative domain excludes these corrections,
New Hampshire's prohibition on offsetting wages with a business loss, and
Kentucky's separate prohibition on one business loss offsetting another
business. Separate generated loss properties cover those intentional changes,
including losses belonging to either spouse, children and students, and
Connecticut's and Maryland's rule that a spouse's loss never reduces the
applicant's own earnings. An actual
git-base differential is run separately. A seeded, stratified sample of 200
households supplements the smaller Hypothesis batches, including spouses and
disabled children.

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
BUSINESS_SOURCES = (
    "self_employment_income",
    "sstb_self_employment_income",
    "farm_operations_income",
    "partnership_self_employment_net_earnings",
)
STATES = (
    "TX",
    "CA",
    "CO",
    "CT",
    "KY",
    "MD",
    "MN",
    "MT",
    "NC",
    "NH",
    "NJ",
    "NV",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SD",
    "VA",
    "VT",
    "WI",
    "WY",
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
    "ct_ssp_own_earned_income",
    "ky_ssp_countable_income",
    "ky_ssp_earned_income",
    "md_paa_countable_income",
    "mn_msa_net_income_eligible",
    "mn_msa_gross_income",
    "mn_msa_person",
    "mt_ssp",
    "nc_sa_countable_income",
    "nh_ssp_countable_income",
    "nj_ssp",
    "nv_oss",
    "ny_ssp",
    "oh_rss_countable_income",
    "ok_ssp_countable_income",
    "ok_ssp_own_countable_income",
    "ok_ssp_spouse_child_allocation",
    "or_ssp_countable_income",
    "pa_ssp",
    "ri_ssp",
    "sd_ssp_care",
    "sd_ssp_independent",
    "tx_ssi_state_supplement_eligible",
    "va_ag_countable_income",
    "vt_aabd_ep_countable_income",
    "vt_aabd_federal",
    "wi_cts_gross_earned_income",
    "wy_ssp_eligible",
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
@example(batch=[(12_000, -6_000, 12_000, "farm_operations_income", True)])
@given(
    batch=st.lists(
        st.tuples(
            st.integers(0, 30_000),
            st.integers(-40_000, 40_000),
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
def unearned_income_with_losses(draw):
    adults = [_person(interest_income=draw(st.integers(241, 24_000)))]
    if draw(st.booleans()):
        adults.append(
            _person(
                age=draw(st.sampled_from((60, 67))),
                interest_income=draw(st.integers(241, 24_000)),
            )
        )
    losses = deepcopy(adults)
    # Every generated household has a loss; either spouse can own it, and
    # both can have losses. Nobody has positive earnings in either version,
    # so total countable income consists entirely of countable unearned income.
    loss_owner = draw(st.integers(0, len(adults) - 1))
    for i, adult in enumerate(losses):
        if i == loss_owner or draw(st.booleans()):
            adult[draw(st.sampled_from(BUSINESS_SOURCES))] = -draw(
                st.integers(1, 40_000)
            )
    state = draw(st.sampled_from(STATES))
    return (
        {"state": state, "adults": adults},
        {"state": state, "adults": losses},
    )


@settings(max_examples=6, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(batch=st.lists(unearned_income_with_losses(), min_size=1, max_size=4))
def test_business_loss_never_reduces_countable_unearned_income(policy, batch):
    simulation = _simulation(
        policy, [household for pair in batch for household in pair]
    )
    for name in ("ssi_unearned_income", "ssi_countable_income"):
        totals = simulation.populations["household"].sum(
            simulation.calculate(name, YEAR)
        )
        pairs = np.asarray(totals).reshape(-1, 2)
        np.testing.assert_array_equal(pairs[:, 0], pairs[:, 1], err_msg=name)


@st.composite
def couples_with_business_losses(draw):
    loss_owner = draw(st.integers(0, 1))
    adults = []
    for i in range(2):
        wages = draw(st.integers(0, 30_000))
        premiums = draw(st.integers(0, 40_000))
        # Draw signed final earnings, then obtain them with wages and one
        # business. The selected spouse always has a residual business loss;
        # the other spouse can have a profit or another residual loss.
        earned = draw(
            st.integers(-40_000, -1)
            if i == loss_owner
            else st.integers(-40_000, 40_000)
        )
        business = earned - wages + min(wages, premiums)
        source = draw(st.sampled_from(BUSINESS_SOURCES))
        adults.append(
            _person(
                age=67 if i == 0 else draw(st.sampled_from((60, 67))),
                employment_income=wages,
                pre_tax_health_insurance_premiums=premiums,
                **{source: business},
            )
        )
    return {"state": draw(st.sampled_from(STATES)), "adults": adults}


@settings(max_examples=6, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@example(
    batch=[
        {
            "state": "TX",
            "adults": [
                _person(employment_income=12_000),
                _person(age=60, farm_operations_income=-5_000),
            ],
        },
        {
            "state": "CT",
            "adults": [
                _person(partnership_self_employment_net_earnings=-9_000),
                _person(age=60, employment_income=4_000),
            ],
        },
    ]
)
@given(batch=st.lists(couples_with_business_losses(), min_size=1, max_size=4))
def test_spousal_loss_pool_is_nonnegative_and_conserves_net_earnings(policy, batch):
    simulation = _simulation(policy, batch)
    earned = simulation.calculate("ssi_earned_income", YEAR).reshape(-1, 2)
    after_loss = simulation.calculate("ssi_earned_income_after_spousal_loss", YEAR)
    assert np.all(after_loss >= 0)
    np.testing.assert_array_equal(
        after_loss.reshape(-1, 2).sum(axis=1),
        np.maximum(earned.sum(axis=1), 0),
    )


@st.composite
def ct_md_applicants_with_spouse_losses(draw):
    # The applicant's own earned income is nonnegative: wages cover any own
    # business loss. The ineligible spouse (under 65, not blind or disabled)
    # has a residual business loss in the first version, so SSI applies part
    # of it to the applicant's wages under POMS SI 00820.210 B.2.c, and any
    # loss in the second. Varying the spouse's loss, from any business
    # source, must leave the applicant's state figures unchanged.
    wages = draw(st.integers(0, 40_000))
    applicant = _person(
        age=draw(st.integers(65, 85)),
        employment_income=wages,
        social_security_retirement=draw(st.integers(0, 20_000)),
        **{draw(st.sampled_from(BUSINESS_SOURCES)): draw(st.integers(-wages, 30_000))},
    )
    spouse_wages = draw(st.integers(0, 30_000))
    source = draw(st.sampled_from(BUSINESS_SOURCES))
    spouse_age = draw(st.integers(30, 64))
    losses = (
        spouse_wages + draw(st.integers(1, 40_000)),
        draw(st.integers(0, spouse_wages + 40_000)),
    )
    spouses = [
        _person(age=spouse_age, employment_income=spouse_wages, **{source: -loss})
        for loss in losses
    ]
    state = draw(st.sampled_from(("CT", "MD")))
    return [{"state": state, "adults": [applicant, spouse]} for spouse in spouses]


@settings(max_examples=6, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@example(
    batch=[
        [
            {
                "state": state,
                "adults": [
                    _person(employment_income=12_000),
                    _person(
                        age=60, employment_income=2_000, self_employment_income=-loss
                    ),
                ],
            }
            for loss in (7_000, 30_000)
        ]
        for state in ("CT", "MD")
    ]
)
@given(batch=st.lists(ct_md_applicants_with_spouse_losses(), min_size=1, max_size=4))
def test_spouse_loss_never_reduces_ct_or_md_applicant_earnings(policy, batch):
    simulation = _simulation(
        policy, [household for pair in batch for household in pair]
    )

    def applicant(name):
        # Rows are [applicant, spouse] per household, two households per pair.
        return simulation.calculate(name, YEAR).reshape(-1, 2, 2)[:, :, 0]

    earned = applicant("ssi_earned_income")
    assert np.all(earned >= 0)
    couple = simulation.calculate("ssi_couple_computation_applies", MONTH)
    assert not np.any(couple)
    in_ct = np.array([pair[0]["state"] == "CT" for pair in batch])
    own = applicant("ct_ssp_own_earned_income")
    np.testing.assert_array_equal(own[:, 0], own[:, 1])
    np.testing.assert_array_equal(own[:, 0], np.where(in_ct, earned[:, 0], 0))
    # Holding SSI's spouse-deemed income at zero isolates the applicant's own
    # earnings, which Maryland counts under COMAR 07.03.07.08.
    deemed = applicant("ssi_income_deemed_from_ineligible_spouse")
    unchanged = (deemed == 0).all(axis=1) & ~in_ct
    paa = applicant("md_paa_countable_income")
    np.testing.assert_array_equal(paa[unchanged, 0], paa[unchanged, 1])


@st.composite
def child_and_student_losses(draw):
    wages = draw(st.integers(0, 2_000))
    child = _person(
        age=draw(st.integers(6, 17)),
        interest_income=draw(st.integers(0, 6_000)),
        is_ssi_ineligible_child=True,
    )
    child_with_loss = {
        **child,
        "employment_income": wages,
        draw(st.sampled_from(BUSINESS_SOURCES)): -wages - draw(st.integers(1, 20_000)),
    }
    student_wages = draw(st.integers(0, 12_000))
    student = _person(
        age=draw(st.integers(18, 21)),
        employment_income=student_wages,
        is_ssi_blind_or_disabled_working_student_exclusion_eligible=True,
        **{
            draw(st.sampled_from(BUSINESS_SOURCES)): -student_wages
            - draw(st.integers(1, 30_000))
        },
    )
    state = draw(st.sampled_from(STATES))
    return (
        {"state": state, "adults": [_person(age=45)], "children": [child]},
        {
            "state": state,
            "adults": [_person(age=45)],
            "children": [child_with_loss],
        },
        {"state": state, "adults": [student]},
    )


@settings(max_examples=6, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(batch=st.lists(child_and_student_losses(), min_size=1, max_size=4))
def test_residual_loss_cannot_raise_child_allocation_or_negate_student_exclusion(
    policy, batch
):
    simulation = _simulation(
        policy, [household for group in batch for household in group]
    )
    allocations = simulation.populations["household"].sum(
        simulation.calculate("ssi_ineligible_child_allocation", YEAR)
    )
    allocations = np.asarray(allocations).reshape(-1, 3)
    # Compare against zero earned income: a residual business loss cannot
    # offset the child's unearned income or enlarge its allocation.
    np.testing.assert_array_equal(allocations[:, 0], allocations[:, 1])
    exclusions = simulation.calculate(
        "ssi_blind_or_disabled_working_student_exclusion", YEAR
    )
    assert np.all(exclusions >= 0)
    # Every eligible student's signed earnings are negative in this batch.
    np.testing.assert_array_equal(exclusions, np.zeros_like(exclusions))


@st.composite
def nonpositive_combined_business_income(draw):
    businesses = [draw(st.integers(-20_000, 20_000)) for _ in range(3)]
    businesses.append(-sum(businesses) - draw(st.integers(0, 20_000)))
    return (
        draw(st.integers(0, 50_000)),
        draw(st.booleans()),
        businesses,
        draw(st.sampled_from(tuple(state for state in STATES if state != "NH"))),
    )


@settings(max_examples=6, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@example(batch=[(12_000, False, [4_000, 0, -6_000, 0], "TX")])
@given(batch=st.lists(nonpositive_combined_business_income(), min_size=1, max_size=4))
def test_nh_nonpositive_combined_business_income_preserves_wages_only_value(
    policy, batch
):
    households = []
    for wages, blind, businesses, other_state in batch:
        person = _person(
            employment_income=wages,
            is_blind=blind,
            # Hold federal SSI at zero so its permitted wage-loss offset
            # cannot conceal New Hampshire's separate earned-income rule.
            takes_up_ssi_if_eligible=False,
            ssi_unearned_income=0,
        )
        with_businesses = {**person, **dict(zip(BUSINESS_SOURCES, businesses))}
        households.extend(
            (
                {"state": "NH", "adults": [person]},
                {"state": "NH", "adults": [with_businesses]},
                {"state": other_state, "adults": [with_businesses]},
            )
        )
    simulation = _simulation(policy, households)
    countable = simulation.calculate("nh_ssp_countable_income", MONTH).reshape(-1, 3)
    np.testing.assert_array_equal(countable[:, 0], countable[:, 1])
    np.testing.assert_array_equal(countable[:, 2], np.zeros(len(batch)))


@st.composite
def separate_business_profits_and_losses(draw):
    # Every generated case has both a profit and a loss. Permuting sources
    # exercises each business's floor, including farm and partnership inputs.
    businesses = draw(
        st.permutations(
            (
                draw(st.integers(1, 40_000)),
                -draw(st.integers(1, 40_000)),
                draw(st.integers(-40_000, 40_000)),
                draw(st.integers(-40_000, 40_000)),
            )
        )
    )
    return (
        draw(st.integers(0, 60_000)),
        draw(st.integers(-10_000, 100_000)),
        businesses,
        draw(st.sampled_from(tuple(state for state in STATES if state != "KY"))),
    )


@settings(max_examples=6, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@example(batch=[(12_000, 0, (10_000, 0, -6_000, 0), "NH")])
@given(batch=st.lists(separate_business_profits_and_losses(), min_size=1, max_size=4))
def test_ky_own_earned_income_preserves_each_business_profit(policy, batch):
    households = []
    expected = []
    for wages, premiums, businesses, other_state in batch:
        person = _person(
            employment_income=wages,
            pre_tax_health_insurance_premiums=premiums,
            **dict(zip(BUSINESS_SOURCES, businesses)),
        )
        households.extend(
            (
                {"state": "KY", "adults": [person]},
                {"state": other_state, "adults": [person]},
            )
        )
        expected.extend(
            (
                wages
                - min(wages, max(premiums, 0))
                + sum(max(profit, 0) for profit in businesses),
                0,
            )
        )
    simulation = _simulation(policy, households)
    np.testing.assert_array_equal(
        simulation.calculate("ky_ssp_earned_income", YEAR), expected
    )


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
