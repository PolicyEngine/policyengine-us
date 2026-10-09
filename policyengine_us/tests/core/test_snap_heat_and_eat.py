"""Reform compatibility invariants for the federal heat-and-eat restriction.

YAML covers individual policy examples. This test compares a parameter reform
that restores the former rule against its baseline, across a vectorized grid.
It detects unintended changes to other states and expense-based eligibility,
and checks fallback against matched households with state deeming disabled.
Only one reform simulation and its baseline are constructed for all dates.
"""

from itertools import product

import numpy as np
from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation


# All SNAP-covered state codes: 50 states, DC, Guam, and the Virgin Islands.
# Other StateCode enum members do not have SNAP utility allowance parameters.
SNAP_STATES = tuple(
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN "
    "MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA "
    "WA WV WI WY DC GU VI".split()
)
PERIODS = ("2025-06", "2025-07", "2025-08", "2026-01")


class LegacyHeatAndEat(Reform):
    def apply(self):
        def modify(parameters):
            parameters.gov.usda.snap.income.deductions.utility.heat_and_eat_requires_elderly_disabled.update(
                start=instant("2025-07-04"),
                stop=instant("2100-12-31"),
                value=False,
            )
            return parameters

        self.modify_parameters(modify)


def _household_grid():
    situation = {
        entity: {}
        for entity in (
            "people",
            "marital_units",
            "tax_units",
            "spm_units",
            "families",
            "households",
        )
    }
    facts = []
    fallback_indices = {}

    def add(state, status, heating, bills, reference=False):
        index = len(facts)
        key = f"case_{index}"
        members = [key]

        def annual(value):
            return {"2025": value, "2026": value}

        person = {
            "age": annual(60 if status == "elderly" else 40),
            # The broad disability flag alone must not qualify under USDA rules.
            "is_disabled": annual(True),
        }
        if status == "ssdi":
            person["social_security_disability"] = annual(1_200)
        situation["people"][key] = person
        for entity in ("marital_units", "tax_units", "families"):
            situation[entity][key] = {"members": members}
        spm_unit = {"members": members}
        if heating:
            spm_unit["heating_cooling_expense"] = annual(1_200)
        if bills == "phone":
            spm_unit["phone_expense"] = annual(360)
        elif bills == "two":
            spm_unit["pre_subsidy_electricity_expense"] = annual(600)
            spm_unit["water_expense"] = annual(300)
        if reference:
            # Matched control: derive expense-based fallback through the
            # existing allowance formulas without duplicating those formulas.
            spm_unit["snap_state_using_standard_utility_allowance"] = {
                month: False for month in PERIODS
            }
            fallback_indices[(state, bills)] = index
        situation["spm_units"][key] = spm_unit
        situation["households"][key] = {
            "members": members,
            "state_code": annual(state),
        }
        facts.append((state, status, heating, bills, reference))

    for state, status, heating, bills in product(
        SNAP_STATES,
        ("ordinary", "elderly", "ssdi"),
        (False, True),
        ("none", "phone", "two"),
    ):
        add(state, status, heating, bills)
    for state, bills in product(SNAP_STATES, ("none", "phone", "two")):
        add(state, "ordinary", False, bills, reference=True)
    controls = np.array(
        [fallback_indices[(state, bills)] for state, _, _, bills, _ in facts]
    )
    return situation, facts, controls


def test_heat_and_eat_reform_preserves_other_utility_allowance_paths():
    situation, facts, controls = _household_grid()
    legacy = Simulation(situation=situation, reform=LegacyHeatAndEat)
    fixed = legacy.baseline
    parameters = fixed.tax_benefit_system.parameters

    def path(date):
        return parameters(date).gov.usda.snap.income.deductions.utility

    assert not bool(path("2025-07-03").heat_and_eat_requires_elderly_disabled)
    assert bool(path("2025-07-04").heat_and_eat_requires_elderly_disabled)

    ordinary = np.array([status == "ordinary" for _, status, _, _, _ in facts])
    heating = np.array([heat for _, _, heat, _, _ in facts])
    bill_style = np.array([bills for _, _, _, bills, _ in facts])

    for month in PERIODS:
        legacy_type = legacy.calculate(
            "snap_utility_allowance_type", month
        ).decode_to_str()
        fixed_type = fixed.calculate(
            "snap_utility_allowance_type", month
        ).decode_to_str()
        legacy_allowance = legacy.calculate("snap_utility_allowance", month)
        fixed_allowance = fixed.calculate("snap_utility_allowance", month)
        state_deeming = fixed.calculate(
            "snap_state_using_standard_utility_allowance", month
        ).astype(bool)
        np.testing.assert_array_equal(
            state_deeming,
            legacy.calculate("snap_state_using_standard_utility_allowance", month),
        )
        # Check the fixture's SNAP status independently of the allowance so
        # eligibility or disability-definition changes cannot hide the defect.
        np.testing.assert_array_equal(
            fixed.calculate("has_snap_elderly_disabled_member", month), ~ordinary
        )
        np.testing.assert_array_equal(
            fixed.calculate("is_snap_excluded_member", month), False
        )

        # The former rule grants SUA whenever the state deems a heating cost.
        np.testing.assert_array_equal(legacy_type[state_deeming], "SUA")
        if month in ("2025-06", "2025-07"):
            # July is evaluated at the start of the month; the legal parameter
            # changes on July 4, making August the first full affected month.
            np.testing.assert_array_equal(fixed_type, legacy_type)
            np.testing.assert_allclose(fixed_allowance, legacy_allowance)
            continue

        affected = state_deeming & ordinary & ~heating
        assert affected.any()
        preserved = ~affected
        np.testing.assert_array_equal(fixed_type[preserved], legacy_type[preserved])
        np.testing.assert_allclose(
            fixed_allowance[preserved], legacy_allowance[preserved]
        )

        # Affected households match expense-only controls, including states
        # with and without a two-utility LUA. Removing deeming never raises SUA.
        np.testing.assert_array_equal(
            fixed_type[affected], fixed_type[controls[affected]]
        )
        np.testing.assert_allclose(
            fixed_allowance[affected], fixed_allowance[controls[affected]]
        )
        np.testing.assert_array_equal(
            fixed_type[affected & (bill_style == "none")], "NONE"
        )
        np.testing.assert_array_equal(
            fixed_type[affected & (bill_style == "phone")], "IUA"
        )
        assert set(fixed_type[affected]) == {"NONE", "IUA", "LUA"}
        assert np.all(fixed_allowance <= legacy_allowance + 1e-6)
