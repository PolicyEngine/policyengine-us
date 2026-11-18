"""Exercise the in_effect activation path of the Vermont H.794 surcharge reform.

The YAML tests apply the reform through the module-level ``bypass=True``
object (``vt_fair_share``), so they never run the non-bypass branch of
``create_vt_fair_share_reform`` or its registration in
``create_structural_reforms_from_parameters``. That is the path the app and
API take when a user sets ``gov.contrib.states.vt.fair_share.in_effect``. The
factory looks at the period and the next four years and returns a ``Reform``
subclass if the toggle is true in any of them, or ``None`` otherwise.

As in ``test_dependent_exemption_reform_activation.py``, only the
``gov.contrib.states`` subtree is cloned, and the copied root's ``parent``
back-reference is cleared so updates stay contained without mutating the
global parameter tree. No test builds a tax-benefit system or copies the whole
parameter tree: deep-copying ``system.parameters`` walks the full tree (~1 GB
peak), while the cloned subtree peaks at a few MB.
"""

from types import SimpleNamespace

import pytest

from policyengine_core.reforms import Reform
from policyengine_us.reforms import create_structural_reforms_from_parameters
from policyengine_us.reforms.states.vt.fair_share.vt_fair_share_reform import (
    create_vt_fair_share_reform,
)
from policyengine_us.system import system

YEAR = 2026
PERIOD = f"{YEAR}-01-01"
# The factory checks the period and the next four years.
LOOKAHEAD_YEARS = 5
REFORM_VARIABLES = {
    "vt_fair_share_surcharge",
    "vt_income_tax_before_refundable_credits",
}


def _states_with_in_effect(**update):
    # Clone ONLY gov.contrib.states and sever the copy from its parent, so the
    # in_effect update below neither escapes into nor copies the global tree.
    states_copy = system.parameters.gov.contrib.states.clone()
    states_copy.parent = None
    states_copy.vt.fair_share.in_effect.update(value=True, **update)
    return states_copy


def _contrib_states_only(states):
    # The factory reads only gov.contrib.states.vt.fair_share, so a thin
    # namespace exposing the copied subtree is sufficient.
    return SimpleNamespace(gov=SimpleNamespace(contrib=SimpleNamespace(states=states)))


class _ParameterView:
    """Delegate to a parameter node, with some of its children replaced."""

    def __init__(self, node, **children):
        self._node = node
        self.__dict__.update(children)

    def __getattr__(self, name):
        return getattr(self._node, name)

    def __call__(self, *args, **kwargs):
        return self._node(*args, **kwargs)


def _global_tree_with_states(states):
    # create_structural_reforms_from_parameters calls every contrib factory.
    # They all read the global tree (not copied, not modified) except under
    # gov.contrib.states, which comes from the cloned subtree.
    root = system.parameters
    return _ParameterView(
        root,
        gov=_ParameterView(
            root.gov,
            contrib=_ParameterView(root.gov.contrib, states=states),
        ),
    )


class _RecordingSystem:
    """Stands in for the system a Reform edits; records updated variables."""

    def __init__(self):
        self.updated_variables = set()

    def update_variable(self, variable):
        self.updated_variables.add(variable.__name__)

    def __getattr__(self, name):
        # Any other edit by another active structural reform is not under test.
        return lambda *args, **kwargs: None


def _variables_updated_by(reform):
    recorder = _RecordingSystem()
    reform.apply(recorder)
    return recorder.updated_variables


def _assert_reform_subclass(result):
    assert isinstance(result, type) and issubclass(result, Reform), (
        f"expected a Reform subclass, got {result!r}"
    )


def test__given_default_parameters__then_factory_returns_none():
    # in_effect is false for every year by default; the factory only reads it.
    assert create_vt_fair_share_reform(system.parameters, PERIOD) is None


@pytest.mark.parametrize("years_ahead", range(LOOKAHEAD_YEARS))
def test__given_in_effect_true_within_lookahead__then_factory_returns_reform(
    years_ahead,
):
    # in_effect is true only in one year: the period itself (0) or up to four
    # years later.
    states = _states_with_in_effect(period=f"year:{YEAR + years_ahead}:1")

    result = create_vt_fair_share_reform(_contrib_states_only(states), PERIOD)

    _assert_reform_subclass(result)
    assert _variables_updated_by(result) == REFORM_VARIABLES


@pytest.mark.parametrize("years_ahead", [LOOKAHEAD_YEARS, LOOKAHEAD_YEARS + 5])
def test__given_in_effect_true_only_beyond_lookahead__then_factory_returns_none(
    years_ahead,
):
    # in_effect is false through the fifth year and true from then on.
    states = _states_with_in_effect(start=f"{YEAR + years_ahead}-01-01")

    result = create_vt_fair_share_reform(_contrib_states_only(states), PERIOD)

    assert result is None


def test__given_in_effect_true__then_structural_reforms_include_vt_fair_share():
    baseline = create_structural_reforms_from_parameters(system.parameters, PERIOD)
    assert not REFORM_VARIABLES & _variables_updated_by(baseline)

    states = _states_with_in_effect(period=f"year:{YEAR}:1")
    combined = create_structural_reforms_from_parameters(
        _global_tree_with_states(states), PERIOD
    )

    assert REFORM_VARIABLES <= _variables_updated_by(combined)
