"""Exercise how the SNAP broad-based categorical eligibility reform activates.

The YAML cases in ``abolish_snap_bbce.yaml`` apply the reform through the
module-level ``bypass=True`` object, and the YAML runner sets a parameter for
every year from 2000 to 2039. So they cannot reach two things:

- the non-bypass branch of ``create_abolish_snap_bbce_reform``, which is the
  path the app and API take when a user sets
  ``gov.contrib.snap.abolish_bbce.in_effect``; and
- a switch that starts on a date, which the formula reads for each month.

The factory tests clone only the ``gov.contrib.snap`` subtree and clear its
``parent`` back-reference, as ``test_vt_fair_share_reform_activation.py`` does,
so they build no tax-benefit system. The two simulation tests each build one
reformed system for a single household.
"""

from types import SimpleNamespace

import pytest

from policyengine_core.reforms import Reform
from policyengine_us import Simulation
from policyengine_us.reforms.snap.abolish_snap_bbce import (
    create_abolish_snap_bbce_reform,
)
from policyengine_us.system import DEFAULT_START_DATE, system
from policyengine_us.tools.parameters import STRUCTURAL_REFORM_CHECK_YEARS

IN_EFFECT = "gov.contrib.snap.abolish_bbce.in_effect"
START_YEAR = int(DEFAULT_START_DATE[:4])


def _parameters_with_in_effect(**update):
    # Clone ONLY gov.contrib.snap and sever the copy from its parent, so the
    # update neither escapes into nor copies the global parameter tree.
    snap_copy = system.parameters.gov.contrib.snap.clone()
    snap_copy.parent = None
    snap_copy.abolish_bbce.in_effect.update(value=True, **update)
    return SimpleNamespace(gov=SimpleNamespace(contrib=SimpleNamespace(snap=snap_copy)))


class _RecordingSystem:
    """Stands in for the system a Reform edits; records updated variables."""

    def __init__(self):
        self.updated_variables = set()

    def update_variable(self, variable):
        self.updated_variables.add(variable.__name__)


def test__given_default_parameters__then_factory_returns_none():
    assert (
        create_abolish_snap_bbce_reform(system.parameters, DEFAULT_START_DATE) is None
    )


@pytest.mark.parametrize("years_ahead", [0, STRUCTURAL_REFORM_CHECK_YEARS - 1])
def test__given_in_effect_true_within_lookahead__then_factory_returns_reform(
    years_ahead,
):
    parameters = _parameters_with_in_effect(period=f"year:{START_YEAR + years_ahead}:1")

    result = create_abolish_snap_bbce_reform(parameters, DEFAULT_START_DATE)

    assert isinstance(result, type) and issubclass(result, Reform)
    recorder = _RecordingSystem()
    result.apply(recorder)
    assert recorder.updated_variables == {"meets_snap_categorical_eligibility"}


def test__given_in_effect_true_only_beyond_lookahead__then_factory_returns_none():
    parameters = _parameters_with_in_effect(
        start=f"{START_YEAR + STRUCTURAL_REFORM_CHECK_YEARS}-01-01"
    )

    assert create_abolish_snap_bbce_reform(parameters, DEFAULT_START_DATE) is None


def _washington_family_simulation(year, wages, in_effect_values):
    # A working parent, a second adult and a child in Washington, which confers
    # broad-based categorical eligibility up to 200% of the poverty guideline.
    # The app applies the switch the same way: a dated Reform.from_dict, with
    # the default start_instant.
    situation = {
        "people": {
            "person1": {
                "age": {year: 35},
                "employment_income": {year: wages},
                "pre_subsidy_rent": {year: 24_000},
            },
            "person2": {"age": {year: 33}},
            "person3": {"age": {year: 8}},
        },
        "spm_units": {"spm_unit": {"members": ["person1", "person2", "person3"]}},
        "households": {
            "household": {
                "members": ["person1", "person2", "person3"],
                "state_code": {year: "WA"},
            }
        },
    }
    reform = Reform.from_dict({IN_EFFECT: in_effect_values}, country_id="us")
    return Simulation(situation=situation, reform=reform)


def test__given_switch_starts_mid_year__then_reform_applies_from_that_month():
    # The household of abolish_snap_bbce.yaml Case 8: $3,500 a month is above
    # the $2,960 federal gross limit for FY2027, and the allotment is $245.
    simulation = _washington_family_simulation(
        2027, 42_000, {"2027-07-01.2100-12-31": True}
    )

    assert simulation.calculate("meets_snap_categorical_eligibility", "2027-06")[0]
    assert simulation.calculate("snap", "2027-06")[0] == pytest.approx(245, abs=0.01)
    assert not simulation.calculate("meets_snap_categorical_eligibility", "2027-07")[0]
    assert simulation.calculate("snap", "2027-07")[0] == 0


def test__given_switch_starts_five_years_after_start_instant__then_reform_applies():
    # 2029 is the sixth year from the default start_instant, so a factory that
    # checked five years would leave the reform out. Dollar amounts for 2029
    # depend on projected guidelines and allotments, so this checks only which
    # tests the family meets and that the benefit is zero.
    simulation = _washington_family_simulation(
        2029, 44_000, {"2029-01-01.2100-12-31": True}
    )

    assert not simulation.calculate("meets_snap_gross_income_test", "2029-01")[0]
    assert simulation.calculate("is_tanf_non_cash_eligible", "2029-01")[0]
    assert not simulation.calculate("meets_snap_categorical_eligibility", "2029-01")[0]
    assert simulation.calculate("snap", "2029-01")[0] == 0
