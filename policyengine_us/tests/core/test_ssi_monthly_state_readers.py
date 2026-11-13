"""Check Maryland PAA and California SSP against changes to one month's ISM."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_core.periods import period as make_period
from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


YEAR = "2024"
MONTHS = tuple(f"{YEAR}-{month:02d}" for month in range(1, 13))
VARIABLES = (
    "md_paa_countable_income",
    "md_paa_imputed_federal_ssi",
    "md_paa",
    "ca_state_supplement_person",
)


def _situation(profiles, annual_earned, annual_unearned):
    situation = {
        group: {}
        for group in (
            "people",
            "households",
            "tax_units",
            "marital_units",
            "families",
            "spm_units",
        )
    }
    rows = {}
    for name, profile in profiles.items():
        for state, citizenship in (
            ("MD", "CITIZEN"),
            ("MD", "LEGAL_PERMANENT_RESIDENT"),
            ("CA", "CITIZEN"),
        ):
            unit = f"{name}_{state}_{citizenship}"
            person = f"{unit}_head"
            members = [person]
            rows[name, state, citizenship] = len(situation["people"])
            values = {
                "age": {YEAR: 70},
                "is_tax_unit_head": {YEAR: True},
                "immigration_status": {YEAR: citizenship},
                "is_ssi_qualified_noncitizen": {YEAR: False},
                "ssi_earned_income": {YEAR: annual_earned},
                "ssi_unearned_income": {YEAR: annual_unearned},
                "ssi_in_kind_support_and_maintenance": dict(zip(MONTHS, profile)),
            }
            if state == "MD":
                values.update(
                    md_paa_eligible={YEAR: True},
                    md_paa_total_cost_of_care={YEAR: 18_000},
                )
            else:
                # Hold federal SSI and the couple's income fixed to isolate
                # the supplement's own-income reader for a CAPI spouse.
                values.update(
                    ssi={YEAR: 7_200},
                    ssi_countable_income={YEAR: 0},
                )
            situation["people"][person] = values
            if state == "CA":
                spouse = f"{unit}_spouse"
                members.append(spouse)
                situation["people"][spouse] = {
                    "age": {YEAR: 68},
                    "is_tax_unit_spouse": {YEAR: True},
                    "immigration_status": {YEAR: "LEGAL_PERMANENT_RESIDENT"},
                    "ssi_qualifying_quarters_earnings": {YEAR: 39},
                    "ssi_countable_income": {YEAR: 0},
                }
            for group in (
                "households",
                "tax_units",
                "marital_units",
                "families",
                "spm_units",
            ):
                situation[group][unit] = {"members": members}
            situation["households"][unit].update(
                state_code={YEAR: state},
                living_arrangements_allow_for_food_preparation={YEAR: True},
            )
    return situation, rows


def _monthly(simulation, variable):
    return np.stack([simulation.calculate(variable, month) for month in MONTHS])


@settings(max_examples=8, deadline=None, database=None, derandomize=True)
@given(
    ism=st.integers(20, 200),
    extra=st.integers(1, 100),
    annual_earned=st.integers(0, 1_200),
    annual_unearned=st.integers(0, 2_400),
)
def test_state_readers_keep_a_december_ism_change_in_december(
    ism, extra, annual_earned, annual_unearned
):
    situation, rows = _situation(
        {"constant": [ism] * 12, "changed": [ism] * 11 + [ism + extra]},
        annual_earned,
        annual_unearned,
    )
    simulation = Simulation(tax_benefit_system=system, situation=situation)
    results = {name: _monthly(simulation, name) for name in VARIABLES}

    for name, values in results.items():
        assert np.all(values >= 0)
        np.testing.assert_allclose(
            simulation.calculate(name, YEAR), values.sum(axis=0), atol=0.01
        )
        for state, citizenship in (
            ("MD", "CITIZEN"),
            ("MD", "LEGAL_PERMANENT_RESIDENT"),
            ("CA", "CITIZEN"),
        ):
            constant = rows["constant", state, citizenship]
            changed = rows["changed", state, citizenship]
            np.testing.assert_allclose(
                values[:11, constant], values[:11, changed], atol=0.01
            )

    for citizenship in ("CITIZEN", "LEGAL_PERMANENT_RESIDENT"):
        constant = rows["constant", "MD", citizenship]
        changed = rows["changed", "MD", citizenship]
        countable = results["md_paa_countable_income"][-1]
        # ISM already uses the whole $20 exclusion, so each extra dollar
        # increases this month's countable income by one dollar.
        assert countable[changed] - countable[constant] == pytest.approx(
            extra, abs=0.01
        )
        imputed = results["md_paa_imputed_federal_ssi"][-1]
        payment = results["md_paa"][-1]
        if citizenship == "CITIZEN":
            assert imputed[constant] - imputed[changed] == pytest.approx(
                extra, abs=0.01
            )
            # Federal SSI offsets the income change while both amounts
            # remain below the federal benefit rate.
            assert payment[changed] == pytest.approx(payment[constant], abs=0.01)
        else:
            assert imputed[constant] == imputed[changed] == 0
            assert payment[constant] - payment[changed] == pytest.approx(
                extra, abs=0.01
            )

    constant = rows["constant", "CA", "CITIZEN"]
    changed = rows["changed", "CA", "CITIZEN"]
    payment = results["ca_state_supplement_person"][-1]
    assert payment[constant] - payment[changed] == pytest.approx(extra, abs=0.011)


@settings(max_examples=6, deadline=None, database=None, derandomize=True)
@given(
    ism=st.integers(0, 400),
    annual_earned=st.integers(0, 24_000),
    annual_unearned=st.integers(0, 12_000),
)
def test_constant_ism_keeps_the_annual_exclusion_result(
    ism, annual_earned, annual_unearned
):
    situation, rows = _situation(
        {"constant": [ism] * 12}, annual_earned, annual_unearned
    )
    simulation = Simulation(tax_benefit_system=system, situation=situation)
    # Constant monthly income must retain the existing annual computation.
    annual_countable = _apply_ssi_exclusions(
        np.array([annual_earned]),
        np.array([annual_unearned + 12 * ism]),
        simulation.tax_benefit_system.parameters,
        make_period(YEAR),
    )[0]
    countable = annual_countable / 12
    for citizenship in ("CITIZEN", "LEGAL_PERMANENT_RESIDENT"):
        index = rows["constant", "MD", citizenship]
        np.testing.assert_allclose(
            _monthly(simulation, "md_paa_countable_income")[:, index],
            countable,
            atol=0.01,
        )

    index = rows["constant", "CA", "CITIZEN"]
    payment = _monthly(simulation, "ca_state_supplement_person")[:, index]
    # POMS SI 01415.056 B.2.a gives the 2024 aged standard of $1,182.94.
    # Federal administration rounds a positive balance and pays at least $1.
    # https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415056
    balance = max(1_182.94 - 600 - countable, 0)
    if balance == 0:
        np.testing.assert_allclose(payment, 0, atol=0.01)
    else:
        assert np.all(payment >= min(balance, 1))
        np.testing.assert_allclose(payment, max(balance, 1), atol=0.011)


def _maryland_reference_countable(monthly_earned, monthly_unearned):
    # COMAR 07.03.07.08(A) disregards $20 of unearned income, then $65 and
    # one-half of the remaining earned income, in any month. PAA Manual 900
    # applies the part of the $20 that unearned income under $20 leaves
    # unused to earnings.
    # https://regs.maryland.gov/us/md/exec/comar/07.03.07.08
    general = min(20, monthly_unearned)
    return monthly_unearned - general + max(monthly_earned - 65 - (20 - general), 0) / 2


@settings(max_examples=5, deadline=None, database=None, derandomize=True)
@given(
    ism=st.integers(0, 19),
    extra=st.integers(1, 19),
    annual_earned=st.integers(0, 2_400),
)
def test_state_readers_keep_a_small_ism_exclusion_in_its_month(
    ism, extra, annual_earned
):
    # With ISM under $20 and no other unearned income, the unused part of
    # the $20 exclusion reduces that month's earnings and no other month's.
    profiles = {"constant": [ism] * 12, "changed": [ism] * 11 + [ism + extra]}
    situation, rows = _situation(profiles, annual_earned, 0)
    simulation = Simulation(tax_benefit_system=system, situation=situation)
    countable = _monthly(simulation, "md_paa_countable_income")
    supplement = _monthly(simulation, "ca_state_supplement_person")

    for name, profile in profiles.items():
        expected = [
            _maryland_reference_countable(annual_earned / 12, monthly_ism)
            for monthly_ism in profile
        ]
        for citizenship in ("CITIZEN", "LEGAL_PERMANENT_RESIDENT"):
            np.testing.assert_allclose(
                countable[:, rows[name, "MD", citizenship]], expected, atol=0.01
            )

    constant = rows["constant", "CA", "CITIZEN"]
    changed = rows["changed", "CA", "CITIZEN"]
    np.testing.assert_allclose(
        supplement[:11, constant], supplement[:11, changed], atol=0.01
    )
