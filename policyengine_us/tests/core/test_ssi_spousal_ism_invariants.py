"""Check SSI spousal deeming across generated income changes.

One vectorized Simulation per draw shares the read-only system singleton.
Independent NumPy calculations preserve main's results without ISM and check
the combined income budget, exclusion bound, and individual payment limit.
Leaf ISM inputs keep its value fixed while each cash income rises. Separate
households increase ISM itself, holding the cash incomes and deeming status
fixed. YAML checks the PMV calculation and worked monthly payments.

These comparisons exercise the Simulation API's monthly and annual input
conversion, deemed-income decomposition, and payment cap. The existing
Rest/core Python group collects this file.
"""

from types import SimpleNamespace

import numpy as np
from policyengine_core.periods import period as make_period
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system


YEAR = 2026
PERIOD = "2026-01"
INDIVIDUAL_FBR = 994
COUPLE_FBR = 1_491
GENERAL_EXCLUSION = 20
EARNED_EXCLUSION = 65
TOLERANCE = 0.01


def _countable(earned, unearned):
    """Apply 416.1112 and 416.1124 to monthly income independently."""
    unused_general = np.maximum(GENERAL_EXCLUSION - unearned, 0)
    return (
        np.maximum(unearned - GENERAL_EXCLUSION, 0)
        + np.maximum(earned - EARNED_EXCLUSION - unused_general, 0) / 2
    )


def _situation(rows):
    situation = {
        plural: {}
        for plural in (
            "people",
            "tax_units",
            "households",
            "marital_units",
            "families",
            "spm_units",
        )
    }
    for index, (
        own_earned,
        own_unearned,
        spouse_earned,
        spouse_unearned,
        ism,
    ) in enumerate(rows):
        claimant, spouse = f"c{index}", f"s{index}"
        situation["people"][claimant] = {
            "age": {YEAR: 70},
            "employment_income": {YEAR: own_earned * 12},
            "pension_income": {YEAR: own_unearned * 12},
            "ssi_in_kind_support_and_maintenance": {
                f"{YEAR}-{month:02}": ism if month == 1 else 0 for month in range(1, 13)
            },
        }
        situation["people"][spouse] = {
            "age": {YEAR: 60},
            "employment_income": {YEAR: spouse_earned * 12},
            "pension_income": {YEAR: spouse_unearned * 12},
        }
        for plural in (
            "tax_units",
            "households",
            "marital_units",
            "families",
            "spm_units",
        ):
            situation[plural][f"u{index}"] = {"members": [claimant, spouse]}
        situation["households"][f"u{index}"]["state_code"] = {YEAR: "TX"}
    return situation


@settings(
    max_examples=5,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    rows=st.lists(
        st.tuples(
            st.integers(0, 2_500),
            st.integers(0, 1_200),
            st.integers(0, 3_500),
            st.integers(0, 900),
            st.integers(0, 25_850),
            st.integers(1, 100_000),
        ),
        min_size=3,
        max_size=3,
    )
)
def test_spousal_ism_preserves_income_and_exclusion_invariants(rows):
    # The final coordinates give ISM and the income increase in cents.
    # Fixed rows retain the wage-only defect, spouse unearned income, and
    # both sides of the claimant's $20 general exclusion.
    cases = [
        *rows,
        (0, 0, 2_000, 0, 25_850, 100),
        (0, 0, 2_000, 100, 25_850, 100),
        (0, 19, 497, 0, 100, 1),
        (0, 20, 498, 0, 100, 1),
        (0, 21, 496, 0, 100, 1),
    ]
    expanded = []
    for own_earned, own_unearned, spouse_earned, spouse_unearned, cents, step in cases:
        expanded.append((own_earned, own_unearned, spouse_earned, spouse_unearned, 0))
        # Keep deeming active as each income coordinate rises. Changing the
        # generated PMV at the deeming threshold requires separate YAML cases.
        supported = np.array(
            [
                own_earned,
                own_unearned,
                max(spouse_earned, 498),
                spouse_unearned,
                cents / 100,
            ],
            dtype=float,
        )
        expanded.append(supported)
        for coordinate in range(5):
            increased = supported.copy()
            increased[coordinate] += step / 100
            expanded.append(increased)

    simulation = Simulation(situation=_situation(expanded), tax_benefit_system=system)
    own_earned, own_unearned, spouse_earned, spouse_unearned, ism = np.array(
        expanded, dtype=float
    ).T
    own_countable = _countable(own_earned, own_unearned + ism)
    combined_countable = _countable(
        own_earned + spouse_earned, own_unearned + spouse_unearned + ism
    )
    applies = spouse_earned + spouse_unearned > COUPLE_FBR - INDIVIDUAL_FBR
    expected_deemed = np.where(
        applies, np.maximum(combined_countable - own_countable, 0), 0
    )
    expected_countable = own_countable + expected_deemed
    individual_payment = np.maximum(INDIVIDUAL_FBR - own_countable, 0)
    expected_payment = np.where(
        applies,
        np.maximum(np.minimum(COUPLE_FBR - combined_countable, individual_payment), 0),
        individual_payment,
    )

    countable = simulation.calculate("ssi_countable_income", PERIOD)[0::2]
    deemed = simulation.calculate(
        "ssi_income_deemed_from_ineligible_spouse_monthly", PERIOD
    )[0::2]
    payment = simulation.calculate("ssi", PERIOD)[0::2]
    cap = simulation.calculate("uncapped_ssi_without_spousal_deeming", PERIOD)[0::2]
    np.testing.assert_allclose(countable, expected_countable, atol=TOLERANCE)
    np.testing.assert_allclose(deemed, expected_deemed, atol=TOLERANCE)
    np.testing.assert_allclose(payment, expected_payment, atol=TOLERANCE)
    assert np.all(payment <= np.maximum(cap, 0) + TOLERANCE)

    zero_ism_own = _countable(own_earned, own_unearned)
    zero_ism_couple = _countable(
        own_earned + spouse_earned, own_unearned + spouse_unearned
    )
    zero_ism_deemed = np.where(
        applies, np.maximum(zero_ism_couple - zero_ism_own, 0), 0
    )
    annual_deemed = simulation.calculate(
        "ssi_income_deemed_from_ineligible_spouse", YEAR
    )[0::2]
    np.testing.assert_allclose(
        annual_deemed, expected_deemed + 11 * zero_ism_deemed, atol=TOLERANCE
    )
    # Calculating the annual aggregate cannot replace February's own budget
    # with one-twelfth of that aggregate.
    february_deemed = simulation.calculate(
        "ssi_income_deemed_from_ineligible_spouse_monthly", f"{YEAR}-02"
    )[0::2]
    np.testing.assert_allclose(february_deemed, zero_ism_deemed, atol=TOLERANCE)

    # Freeze main's no-ISM difference formula independently of current
    # countable or deemed outputs, including its below-threshold path.
    no_ism = np.arange(0, len(expanded), 7)
    original_own = _countable(own_earned[no_ism], own_unearned[no_ism])
    original_couple = _countable(
        own_earned[no_ism] + spouse_earned[no_ism],
        own_unearned[no_ism] + spouse_unearned[no_ism],
    )
    original_deemed = np.where(
        applies[no_ism], np.maximum(original_couple - original_own, 0), 0
    )
    original_countable = original_own + original_deemed
    original_alone = INDIVIDUAL_FBR - original_own
    original_payment = np.maximum(
        np.where(
            applies[no_ism],
            np.minimum(COUPLE_FBR - original_countable, original_alone),
            original_alone,
        ),
        0,
    )
    np.testing.assert_allclose(deemed[no_ism], original_deemed, atol=TOLERANCE)
    np.testing.assert_allclose(
        annual_deemed[no_ism], 12 * original_deemed, atol=TOLERANCE
    )
    np.testing.assert_allclose(countable[no_ism], original_countable, atol=TOLERANCE)
    np.testing.assert_allclose(payment[no_ism], original_payment, atol=TOLERANCE)

    supported_countable = countable.reshape(len(cases), 7)[:, 1:]
    assert np.all(supported_countable[:, 1:] >= supported_countable[:, :1] - TOLERANCE)

    # Remove only the general exclusion from an independent couple budget.
    # Retain the $65 earned exclusion and one-half earned-income disregard.
    without_general = (
        own_unearned
        + spouse_unearned
        + ism
        + np.maximum(own_earned + spouse_earned - EARNED_EXCLUSION, 0) / 2
    )
    supported = np.ones(len(expanded), dtype=bool)
    supported[no_ism] = False
    general_reduction = without_general[supported] - countable[supported]
    assert np.all(general_reduction >= -TOLERANCE)
    assert np.all(general_reduction <= GENERAL_EXCLUSION + TOLERANCE)


def test_legacy_annual_override_replaces_cached_monthly_budgets():
    simulation = Simulation(
        situation=_situation([(0, 0, 2_000, 0, 258.50)]),
        tax_benefit_system=system,
    )
    monthly_name = "ssi_income_deemed_from_ineligible_spouse_monthly"
    annual_name = "ssi_income_deemed_from_ineligible_spouse"
    # January counts $258.50 ISM; February counts none. Annual deeming sums
    # $967.50 + 11 * $957.50 = $11,500 without averaging the ISM correction.
    np.testing.assert_allclose(
        simulation.calculate(monthly_name, PERIOD), [967.50, 0], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        simulation.calculate(annual_name, YEAR), [11_500, 0], atol=TOLERANCE
    )

    # An explicit legacy $2,160 annual input supplies $180 in every month,
    # including months the parent simulation already calculated.
    branch = simulation.get_branch("annual_deemed_override")
    branch.set_input(annual_name, YEAR, [2_160, 0])
    for month in (PERIOD, f"{YEAR}-02"):
        np.testing.assert_allclose(
            branch.calculate(monthly_name, month), [180, 0], atol=TOLERANCE
        )
    # An explicit zero overrides calculated deeming as an amount, too.
    zero_branch = simulation.get_branch("zero_annual_deemed_override")
    zero_branch.set_input(annual_name, YEAR, [0, 0])
    np.testing.assert_array_equal(zero_branch.calculate(monthly_name, PERIOD), [0, 0])
    np.testing.assert_allclose(
        simulation.calculate(monthly_name, PERIOD), [967.50, 0], atol=TOLERANCE
    )
    np.testing.assert_allclose(
        simulation.calculate(monthly_name, f"{YEAR}-02"), [957.50, 0], atol=TOLERANCE
    )


def test_annual_input_adapter_honors_dated_legacy_abolition():
    # Exercise the input adapter without constructing another policy system.
    # Core checks abolition at the requested month before period conversion.
    from policyengine_us.variables.gov.ssa.ssi.eligibility.income._annual_input import (
        annual_input,
    )

    name = "ssi_income_deemed_from_ineligible_spouse"

    class Parameters:
        def __call__(self, period):
            return SimpleNamespace(
                gov=SimpleNamespace(abolitions={name: period.start.month >= 7})
            )

    holder = SimpleNamespace(
        variable=SimpleNamespace(is_neutralized=False, definition_period="year"),
        get_known_branch_periods=lambda: [],
        _record_store=lambda period, sequence_number: None,
    )
    simulation = SimpleNamespace(
        tax_benefit_system=SimpleNamespace(parameters=Parameters()),
        get_holder=lambda variable: holder,
        _user_input_keys=set(),
        _get_visible_branch_names=lambda: [],
    )
    person = SimpleNamespace(simulation=simulation)
    assert annual_input(person, make_period("2026-01"), name) is None
    assert annual_input(person, make_period("2026-07"), name) == 0
