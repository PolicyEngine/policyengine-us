"""The optional calculator leaves the existing model disconnected and unchanged.

The reference removes the new variables and parameter namespaces entirely. It
therefore detects an accidental dependency even when a new variable's default
value happens to be neutral. This is portable in source distributions and CI;
it does not need a second checkout or git at test time. The implementation's
separate source-diff check establishes that legacy formulas/parameters were not
edited. These comparisons exercise their live SSA and downstream dependency
closures, including every intermediate value actually calculated by reference.
"""

from copy import deepcopy

import numpy as np
import pytest
from policyengine_core.reforms import Reform

from policyengine_us import Simulation
from policyengine_us.tools.general import earliest_input_year


CALCULATOR_PREFIXES = ("ss_calculator_", "ss_calculated_")
NEW_PARAMETER_NODES = (
    "gov.contrib.ssa.benefit_levers",
    "gov.contrib.ssa.pia",
    "gov.contrib.congress.s770",
    "gov.ssa.social_security.pia.bend_points",
    "gov.ssa.social_security.cola",
    "gov.ssa.cola_history",
)
YEAR = 2026


class WithoutHouseholdCalculator(Reform):
    """Reconstruct the existing model by removing only this feature's additions."""

    def apply(self):
        self.variables = {
            name: variable
            for name, variable in self.variables.items()
            if not name.startswith(CALCULATOR_PREFIXES)
        }
        for path in NEW_PARAMETER_NODES:
            parent = self.parameters
            *parents, name = path.split(".")
            for part in parents:
                parent = parent.children.get(part)
                if parent is None:
                    break
            if parent is not None and name in parent.children:
                parent.children.pop(name)
                delattr(parent, name)


LEGACY_SSA_OUTPUTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
    "social_security",
    "ss_aime_eligible",
    "ss_aime",
    "ss_claiming_age",
    "ss_covered_earnings_this_year",
    "ss_earnings_test_applicable",
    "ss_earnings_test_reduction",
    "ss_full_retirement_age_months",
    "ss_pia",
    "ss_quarters_of_coverage",
    "ss_retirement_age_adjustment_factor",
    "ss_retirement_benefit_before_earnings_test",
    "ss_retirement_eligible",
)
DOWNSTREAM_OUTPUTS = (
    "taxable_social_security",
    "adjusted_gross_income",
    "income_tax",
    "net_investment_income_tax",
    "medicare_irmaa_magi",
    "medicare_irmaa_magi_two_years_prior",
    "medicare_part_b_premium",
    "ssi",
    "household_net_income",
)


def _situation(age, benefits, earnings=0, investment_income=0, joint=False):
    amounts = dict(zip(LEGACY_SSA_OUTPUTS[:4], benefits))
    person = {
        "age": {YEAR: age},
        "employment_income": {YEAR: earnings},
        "taxable_interest_income": {YEAR: investment_income},
        # Supply the existing intermediate to avoid reconstructing a career;
        # the legacy helper calculations are deliberately still disconnected
        # from the separately supplied public benefit amounts.
        "ss_aime": {YEAR: 5_000},
        "ss_claiming_age": {YEAR: 62},
        **{name: {YEAR: value} for name, value in amounts.items()},
    }
    people = {"worker": person}
    if joint:
        people["spouse"] = {
            "age": {YEAR: age - 2},
            "social_security_retirement": {YEAR: 12_000},
            "ss_aime": {YEAR: 3_000},
            "ss_claiming_age": {YEAR: 65},
        }
    members = list(people)
    return {
        "people": people,
        "tax_units": {
            "tax_unit": {"members": members, "tax_unit_itemizes": {YEAR: False}}
        },
        "spm_units": {"spm_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "marital_units": {"marital_unit": {"members": members}},
        "households": {"household": {"members": members, "state_code": {YEAR: "NY"}}},
    }


def _cached_reference_values(simulation):
    """Capture the whole exercised dependency closure before comparing values."""
    return [
        (name, period, holder.get_array(period).copy())
        for population in simulation.populations.values()
        for name, holder in population._holders.items()
        for period in holder.get_known_periods()
        if holder.get_array(period) is not None
    ]


@pytest.mark.parametrize(
    "situation",
    [
        _situation(45, (0, 0, 0, 0), earnings=50_000),
        _situation(62, (18_000, 0, 0, 0), earnings=33_400),
        _situation(67, (0, 0, 24_000, 0), investment_income=90_000),
        _situation(50, (0, 16_000, 0, 4_000), earnings=2_000),
        _situation(75, (30_000, 0, 0, 0), investment_income=150_000, joint=True),
    ],
    ids=("working", "early-retirement", "survivor", "disability", "own-record-couple"),
)
def test_calculator_off_matches_model_without_feature(situation):
    isolated = Simulation.default_tax_benefit_system_instance.clone()
    isolated.apply_reform_set(WithoutHouseholdCalculator)
    reference = Simulation(
        situation=deepcopy(situation),
        tax_benefit_system=isolated,
        reform=WithoutHouseholdCalculator,
    )
    off_inputs = deepcopy(situation)
    for person in off_inputs["people"].values():
        person["ss_calculator_source"] = "off"
        # An unselected amount must never activate a source by positivity.
        person["ss_calculator_supplied_aime"] = 12_345
        person["ss_calculator_supplied_pia"] = 4_321.0
    actual = Simulation(situation=off_inputs)

    assert not any(
        name.startswith(CALCULATOR_PREFIXES)
        for name in reference.tax_benefit_system.variables
    )
    for name in LEGACY_SSA_OUTPUTS + DOWNSTREAM_OUTPUTS:
        expected = reference.calculate(name, YEAR)
        np.testing.assert_array_equal(
            actual.calculate(name, YEAR), expected, err_msg=name
        )

    # Check every legacy intermediate reached by these outputs, not only the
    # handful of final totals chosen above. Exact equality includes zero inputs.
    for name, period, expected in _cached_reference_values(reference):
        np.testing.assert_array_equal(
            actual.calculate(name, period), expected, err_msg=f"{name} at {period}"
        )
    for name in (
        "ss_calculated_annual_entitlement",
        "ss_calculated_annual_payment",
        "ss_calculated_retirement",
        "ss_calculated_survivors",
    ):
        np.testing.assert_array_equal(actual.calculate(name, YEAR), 0)


@pytest.mark.parametrize("amount", [0, 18_000])
def test_legacy_public_input_and_later_zero_override_survive(amount):
    situation = _situation(70, (amount, 0, 0, 0))
    actual = Simulation(situation=situation)
    np.testing.assert_array_equal(
        actual.calculate("social_security_retirement", YEAR), [amount]
    )
    actual.set_input("social_security_retirement", YEAR, np.array([0]))
    np.testing.assert_array_equal(
        actual.calculate("social_security_retirement", YEAR), [0]
    )


def test_off_unselected_history_does_not_change_irmaa_lookback():
    """Calculator records are not a past-year tax return supplied to the model."""
    situation = _situation(75, (30_000, 0, 0, 0), investment_income=150_000)
    isolated = Simulation.default_tax_benefit_system_instance.clone()
    isolated.apply_reform_set(WithoutHouseholdCalculator)
    reference = Simulation(
        situation=deepcopy(situation),
        tax_benefit_system=isolated,
        reform=WithoutHouseholdCalculator,
    )
    situation["people"]["worker"].update(
        {
            "ss_calculator_source": "off",
            "ss_calculator_annual_earnings": {2020: 50_000},
            "ss_calculator_pre_fra_earnings": {2020: 20_000},
            "ss_calculator_withhold_cola": {2020: True},
        }
    )
    actual = Simulation(situation=situation)
    assert earliest_input_year(reference) == YEAR
    assert earliest_input_year(actual) == YEAR
    for name in (
        "medicare_irmaa_magi_two_years_prior",
        "medicare_part_b_premium",
        "household_net_income",
    ):
        np.testing.assert_array_equal(
            actual.calculate(name, YEAR),
            reference.calculate(name, YEAR),
            err_msg=name,
        )
