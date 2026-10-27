"""PIA-ratio dataset ingress and compatibility with the neutral stacked hooks.

The two-household H5 exercises a dataset column that a situation-only policy
test cannot cover. The differential replaces only C's four factor formulas
with A's original constant-one hooks: all other stacked-base calculations and
the public-column migration remain live. No population microsimulation runs.
"""

from copy import deepcopy

import numpy as np
import pytest
from policyengine_core.data import Dataset
from policyengine_core.reforms import Reform
from policyengine_core.simulations import Simulation as CoreSimulation


YEAR = 2026
COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)
BENEFITS = (*COMPONENTS, "social_security")
DOWNSTREAM = (
    "taxable_social_security",
    "tax_unit_taxable_social_security",
    "adjusted_gross_income",
    "income_tax",
    "household_net_income",
    "ssi_unearned_income",
    "snap_unearned_income",
)
AMOUNTS = ((18_440.64, 0, 0, 0), (12_000, 6_000, 1_200, 300))
GROUP_ENTITIES = ("household", "tax_unit", "spm_unit", "family", "marital_unit")
GROUP_PLURALS = ("households", "tax_units", "spm_units", "families", "marital_units")


def _write_h5(path):
    """Write scored-year public benefits and whole-month claim-age columns."""
    import h5py

    ids = np.array([1, 2])
    columns = {
        "person_id": ids,
        "age": [62, 70],
        "social_security_retirement_claim_age_months": [747, 0],
        "taxable_interest_income": [30_000, 10],
        "state_fips": [48, 48],
    }
    for entity in GROUP_ENTITIES:
        columns[f"person_{entity}_id"] = ids
        columns[f"{entity}_id"] = ids
        columns[f"{entity}_weight"] = [2.0, 3.0]
    for index, component in enumerate(COMPONENTS):
        columns[component] = [amounts[index] for amounts in AMOUNTS]
    with h5py.File(path, "w") as stored:
        for name, values in columns.items():
            stored.create_dataset(f"{name}/{YEAR}", data=values)


def _situation():
    people = {}
    for index, person in enumerate(("retiree", "missing_claim_age")):
        people[person] = {
            "age": {YEAR: (62, 70)[index]},
            "social_security_retirement_claim_age_months": {YEAR: (747, 0)[index]},
            "taxable_interest_income": {YEAR: (30_000, 10)[index]},
            **{
                component: {YEAR: AMOUNTS[index][column]}
                for column, component in enumerate(COMPONENTS)
            },
        }
    result = {"people": people}
    for plural in GROUP_PLURALS:
        result[plural] = {person: {"members": [person]} for person in people}
    for household in result["households"].values():
        household["state_code"] = {YEAR: "TX"}
    return result


@pytest.fixture(scope="module")
def country_system():
    # Share the read-only model; reforms and simulations keep independent state.
    from policyengine_us.system import system

    return system


def _neutral_stacked_base(system):
    """Restore the original A hooks while retaining the complete stacked model."""
    from policyengine_us.model_api import Person, Variable, YEAR

    class NeutralPIARatioHooks(Reform):
        def apply(self):
            for component in COMPONENTS:
                variable = type(
                    f"{component}_pia_ratio_factor",
                    (Variable,),
                    {
                        "value_type": float,
                        "entity": Person,
                        "definition_period": YEAR,
                        "formula": lambda person, period, parameters: 1,
                    },
                )
                self.update_variable(variable)

    return NeutralPIARatioHooks(system)


def _snapshot(simulation):
    requested = {
        name: np.asarray(simulation.calculate(name, YEAR)).copy()
        for name in (*BENEFITS, *DOWNSTREAM)
    }
    # Check intermediates reached by these outputs, not just their final
    # totals. New diagnostic-only values have no counterpart in A's hooks.
    cached = {}
    for population in simulation.populations.values():
        for name, holder in population._holders.items():
            array = holder.get_array(YEAR, simulation.branch_name)
            if array is not None:
                cached[name] = np.asarray(array).copy()
    return requested, cached


@pytest.mark.parametrize("ingress", ("reported_situation", "public_h5"))
def test_all_off_matches_neutral_stacked_base(country_system, tmp_path, ingress):
    """C adds no current-law change on either supported initial-ingress route."""
    if ingress == "public_h5":
        path = tmp_path / "reported_benefits_2026.h5"
        _write_h5(path)
        inputs = {"dataset": Dataset.from_file(path)}
    else:
        inputs = {"situation": _situation()}
        # Explicit reported names are the policy-sensitive route in a situation.
        for person in inputs["situation"]["people"].values():
            for component in COMPONENTS:
                person[f"{component}_reported"] = person.pop(component)

    results = []
    for system in (country_system, _neutral_stacked_base(country_system)):
        simulation_inputs = (
            {"dataset": Dataset.from_file(path)}
            if ingress == "public_h5"
            else deepcopy(inputs)
        )
        simulation = CoreSimulation(
            **simulation_inputs,
            tax_benefit_system=system,
            default_input_period=YEAR,
            default_calculation_period=YEAR,
        )
        requested, cached = _snapshot(simulation)
        for index, component in enumerate(COMPONENTS):
            np.testing.assert_array_equal(
                requested[component],
                np.asarray([amounts[index] for amounts in AMOUNTS], dtype=np.float32),
            )
        results.append((requested, cached))

    current, reference = results
    assert current[0].keys() == reference[0].keys()
    for name in current[0]:
        np.testing.assert_array_equal(
            current[0][name], reference[0][name], err_msg=name
        )
    assert reference[1].keys() <= current[1].keys()
    for name in reference[1]:
        np.testing.assert_array_equal(
            current[1][name], reference[1][name], err_msg=name
        )


def test_supplied_claim_months_load_from_h5_and_drive_inverse(country_system, tmp_path):
    path = tmp_path / "claim_months_2026.h5"
    _write_h5(path)
    reform = Reform.from_dict(
        {
            "gov.contrib.ssa.pia.in_effect": {YEAR: True},
            "gov.contrib.ssa.pia.factors.first": {YEAR: 0.95},
            "gov.contrib.ssa.pia.bend_point_multipliers.first": {YEAR: 1.15},
            "gov.ssa.social_security.pia.bend_points.first": {YEAR: 960},
            "gov.ssa.social_security.pia.bend_points.second": {YEAR: 5785},
        }
    )
    simulation = CoreSimulation(
        dataset=Dataset.from_file(path),
        tax_benefit_system=country_system,
        reform=reform,
        default_input_period=YEAR,
        default_calculation_period=YEAR,
    )
    np.testing.assert_array_equal(
        simulation.calculate("social_security_retirement_claim_age_months", YEAR),
        [747, 0],
    )
    # Core carries stored inputs forward through its ordinary dataset contract;
    # the input has no formula/uprating, and C rebuilds inferred cohorts by year.
    np.testing.assert_array_equal(
        simulation.calculate("social_security_retirement_claim_age_months", YEAR + 1),
        [747, 0],
    )
    adjustment = simulation.calculate(
        "social_security_retirement_pia_ratio_claiming_adjustment", YEAR
    )
    assert adjustment[0] == pytest.approx(0.7125)
    assert adjustment[1] == 0
    aime = simulation.calculate("social_security_retirement_inferred_aime", YEAR)
    assert aime[0] == pytest.approx(5000, abs=0.01)
    lower = simulation.calculate(
        "social_security_retirement_inferred_aime_lower_bound", YEAR
    )
    upper = simulation.calculate(
        "social_security_retirement_inferred_aime_upper_bound", YEAR
    )
    assert lower[0] <= aime[0] < upper[0]
    factors = simulation.calculate("social_security_retirement_pia_ratio_factor", YEAR)
    assert factors[0] == pytest.approx(2295.5 / 2156.8)
    assert factors[1] == 1
    np.testing.assert_array_equal(
        simulation.calculate(
            "social_security_retirement_pia_ratio_own_record_retired_worker", YEAR
        ),
        [True, False],
    )
    flags = np.asarray(
        simulation.calculate(
            "social_security_retirement_pia_ratio_missing_claim_age", YEAR
        )
    )
    np.testing.assert_array_equal(flags, [False, True])
    # Person flags retain the household weights supplied by the projected file.
    weights = np.asarray(simulation.calculate("household_weight", YEAR))
    assert np.dot(flags, weights) == 3
    counts = simulation.calculate(
        "social_security_retirement_pia_ratio_missing_claim_age_count", YEAR
    )
    np.testing.assert_array_equal(counts, [0, 1])
    assert np.dot(counts, weights) == 3
    public = simulation.calculate("social_security_retirement", YEAR)
    assert public[0] == pytest.approx(12 * 0.7125 * 2295.5, abs=0.01)
    assert public[1] == 12_000


def test_claim_months_are_a_pure_annual_input(country_system):
    variable = country_system.variables["social_security_retirement_claim_age_months"]
    assert variable.value_type is int
    assert variable.default_value == 0
    assert not variable.formulas
    assert not getattr(variable, "uprating", None)


def test_named_aime_endpoint_round_trips_after_float32_storage(country_system):
    """A nonterminating inverse must survive storage in the Person holder."""
    from decimal import Decimal
    from fractions import Fraction

    from policyengine_us.tools.social_security.parameters import bend_points_at
    from policyengine_us.tools.social_security.pia import compute_pia

    situation = {
        "people": {
            "retiree": {
                "age": {YEAR: 62},
                "social_security_retirement_reported": {YEAR: 60},
                "social_security_retirement_claim_age_months": {YEAR: 804},
            }
        },
        **{plural: {"group": {"members": ["retiree"]}} for plural in GROUP_PLURALS},
    }
    simulation = CoreSimulation(
        situation=situation,
        tax_benefit_system=country_system,
        default_input_period=YEAR,
        default_calculation_period=YEAR,
    )
    aime = simulation.calculate("social_security_retirement_inferred_aime", YEAR)[0]
    lower = simulation.calculate(
        "social_security_retirement_inferred_aime_lower_bound", YEAR
    )[0]
    upper = simulation.calculate(
        "social_security_retirement_inferred_aime_upper_bound", YEAR
    )[0]
    assert lower == aime
    assert lower < upper
    assert Fraction(float(lower)) >= Fraction(50, 9)
    assert Fraction(float(upper)) >= Fraction(17, 3)
    assert compute_pia(
        float(aime), YEAR, bend_points=bend_points_at(country_system.parameters, YEAR)
    ) == Decimal("5.0")
