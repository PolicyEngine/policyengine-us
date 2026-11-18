"""Unselected history preserves existing calculator, SSA and tax results.

One four-person vector exercises all preexisting calculator sources. The
reference removes only the history feature's additions, so an accidental
dependency on even a neutral new default fails. Every cached reference
intermediate is compared as well as the selected public outputs.
"""

from copy import deepcopy

import numpy as np
from policyengine_core.periods import MONTH
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.tests.unit.test_ss_calculator_differential import (
    DOWNSTREAM_OUTPUTS,
    LEGACY_SSA_OUTPUTS,
    _cached_reference_values,
)
from policyengine_us.tests.unit.test_ss_calculator_engine import _record, _survivor


HISTORY_INPUTS = {
    "ss_calculator_earnings_history",
    "ss_calculator_donut_variant",
}
YEAR = 2026


class WithoutAnnualEarningsHistory(Reform):
    """Keep the existing supplied calculator and all shared SSA policies."""

    def apply(self):
        self.variables = {
            name: variable
            for name, variable in self.variables.items()
            if name not in HISTORY_INPUTS
            and not name.startswith("ss_calculated_history_")
        }
        parent = self.parameters.gov.contrib.ssa
        parent.children.pop("history")
        delattr(parent, "history")


def _mixed_source_situation():
    people = {
        "off": {"ss_calculator_source": "off", "age": {YEAR: 45}},
        "aime": _record(
            "aime-worker",
            ss_calculator_source="aime",
            ss_calculator_supplied_aime=5_000,
            age={YEAR: 62},
        ),
        "pia": _record(
            "pia-worker",
            ss_calculator_birth_date="1959-01-02",
            ss_calculator_eligibility_year=2021,
            ss_calculator_entitlement_month="2024-07",
            ss_calculator_supplied_pia=2_000.2,
            age={YEAR: 67},
        ),
        "survivor": _survivor(age={YEAR: 76}),
    }
    for index, person in enumerate(people.values()):
        person.update(
            employment_income={YEAR: (50_000, 33_400, 0, 0)[index]},
            taxable_interest_income={YEAR: (0, 0, 90_000, 20_000)[index]},
            social_security_retirement={YEAR: (0, 18_000, 30_000, 0)[index]},
            social_security_disability={YEAR: (0, 0, 0, 0)[index]},
            social_security_survivors={YEAR: (0, 0, 0, 24_000)[index]},
            social_security_dependents={YEAR: (0, 0, 0, 0)[index]},
            # Exercise legacy SSA helpers without reconstructing four careers.
            # The pure legacy-history differential covers their annual window.
            ss_aime={YEAR: 5_000},
            ss_claiming_age={YEAR: 62},
        )
    situation = {"people": people}
    for entity in ("tax_units", "families", "spm_units", "marital_units", "households"):
        situation[entity] = {name: {"members": [name]} for name in people}
    for unit in situation["tax_units"].values():
        # Avoid unrelated state/federal itemization optimization.
        unit["tax_unit_itemizes"] = {YEAR: False}
    for household in situation["households"].values():
        household["state_code"] = {YEAR: "NY"}
    return situation


def test_unselected_history_matches_model_without_history_through_all_cached_outputs():
    situation = _mixed_source_situation()
    reference = Simulation(
        situation=deepcopy(situation),
        tax_benefit_system=Simulation.default_tax_benefit_system_instance,
        reform=WithoutAnnualEarningsHistory,
    )
    actual_inputs = deepcopy(situation)
    for person in actual_inputs["people"].values():
        # Neither supplied source is selected. Parsing either value or looking
        # up this nonexistent variant would fail immediately if history leaked
        # into an existing off/AIME/PIA/survivor route.
        person["ss_calculator_earnings_history"] = "{malformed unselected JSON"
        person["ss_calculator_donut_variant"] = "unregistered-unselected-variant"
    actual = Simulation(situation=actual_inputs)

    registry = reference.tax_benefit_system.variables
    assert not HISTORY_INPUTS.intersection(registry)
    assert not any(name.startswith("ss_calculated_history_") for name in registry)
    assert (
        "history"
        not in reference.tax_benefit_system.parameters.gov.contrib.ssa.children
    )
    assert "ss_calculator_source" in registry
    assert "ss_calculated_payment" in registry

    # Discover every existing calculator output, preserving its annual/monthly
    # definition; future additions to the supplied calculator remain covered.
    calculator_outputs = tuple(
        (name, "2026-06" if variable.definition_period == MONTH else YEAR)
        for name, variable in sorted(registry.items())
        if name.startswith("ss_calculated_")
    )
    assert len(calculator_outputs) >= 13
    for name, instant in calculator_outputs:
        expected = reference.calculate(name, instant)
        np.testing.assert_array_equal(
            actual.calculate(name, instant), expected, err_msg=f"{name} at {instant}"
        )
    for name in LEGACY_SSA_OUTPUTS + DOWNSTREAM_OUTPUTS:
        expected = reference.calculate(name, YEAR)
        np.testing.assert_array_equal(
            actual.calculate(name, YEAR), expected, err_msg=name
        )

    closure = _cached_reference_values(reference)
    assert len(closure) > len(calculator_outputs)
    for name, instant, expected in closure:
        np.testing.assert_array_equal(
            actual.calculate(name, instant), expected, err_msg=f"{name} at {instant}"
        )
