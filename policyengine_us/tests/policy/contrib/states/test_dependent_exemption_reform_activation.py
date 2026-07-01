"""Exercise the reform-activation branch of the state dependent-exemption /
dependent-credit reform factories.

The YAML tests for these reforms apply each reform via the ``bypass=True``
module-level object (e.g. ``hi_dependent_exemption_reform``), so the
non-bypass code path inside every ``create_<st>_..._reform_fn`` is never run by
those tests. That path inspects the ``in_effect`` contrib parameter over a
five-year window and returns either a ``Reform`` subclass (when the reform is
in effect) or ``None`` (the default no-op).

This module covers both outcomes for all eleven states in the PR, mirroring how
``reforms/reforms.py`` calls the factories with ``(parameters, period)`` and the
Indiana dynamic-import special case (its package directory ``in`` is a Python
keyword and cannot be imported with a dotted path).

Only the ``gov.contrib.states`` subtree is cloned (module-scoped fixture), and
the copied root's ``parent`` back-reference is cleared so later parameter
updates stay contained. Deep-copying ``system.parameters`` wholesale — or any
subtree without severing ``parent`` — walks the whole tree via that
back-reference (~1 GB peak). Stacked onto the already-large Python suite, that
copy OOM-killed the CI "Rest" runner; the cloned subtree peaks at a few MB
instead.
"""

import importlib
from types import SimpleNamespace

import pytest

from policyengine_core.reforms import Reform
from policyengine_us.system import system


def _load_in_reform_fn():
    # Indiana's module dir is ``in`` (a Python keyword), so it cannot be
    # imported with a dotted ``from .states.in...`` path. Load it dynamically,
    # exactly as reforms/reforms.py does.
    module = importlib.import_module(
        "policyengine_us.reforms.states.in.dependent_exemption."
        "in_dependent_exemption_reform"
    )
    return module.create_in_dependent_exemption_reform_fn


def _load_reform_fn(state, folder, module_name, fn_name):
    if state == "in":
        return _load_in_reform_fn()
    module = importlib.import_module(
        f"policyengine_us.reforms.states.{state}.{folder}.{module_name}"
    )
    return getattr(module, fn_name)


# (state_code, parameter_folder, module_name, factory_fn_name)
# Most states use a ``dependent_exemption`` folder; Arkansas uses
# ``dependent_credit`` (it redirects the shared personal-credit base instead of
# a deduction-style exemption).
STATE_CONFIGS = [
    (
        "ar",
        "dependent_credit",
        "ar_dependent_credit_reform",
        "create_ar_dependent_credit_reform_fn",
    ),
    (
        "hi",
        "dependent_exemption",
        "hi_dependent_exemption_reform",
        "create_hi_dependent_exemption_reform_fn",
    ),
    (
        "in",
        "dependent_exemption",
        "in_dependent_exemption_reform",
        "create_in_dependent_exemption_reform_fn",
    ),
    (
        "md",
        "dependent_exemption",
        "md_dependent_exemption_reform",
        "create_md_dependent_exemption_reform_fn",
    ),
    (
        "mi",
        "dependent_exemption",
        "mi_dependent_exemption_reform",
        "create_mi_dependent_exemption_reform_fn",
    ),
    (
        "ne",
        "dependent_exemption",
        "ne_dependent_exemption_reform",
        "create_ne_dependent_exemption_reform_fn",
    ),
    (
        "oh",
        "dependent_exemption",
        "oh_dependent_exemption_reform",
        "create_oh_dependent_exemption_reform_fn",
    ),
    (
        "ok",
        "dependent_exemption",
        "ok_dependent_exemption_reform",
        "create_ok_dependent_exemption_reform_fn",
    ),
    (
        "vt",
        "dependent_exemption",
        "vt_dependent_exemption_reform",
        "create_vt_dependent_exemption_reform_fn",
    ),
    (
        "wi",
        "dependent_exemption",
        "wi_dependent_exemption_reform",
        "create_wi_dependent_exemption_reform_fn",
    ),
    (
        "wv",
        "dependent_exemption",
        "wv_dependent_exemption_reform",
        "create_wv_dependent_exemption_reform_fn",
    ),
]

PERIOD = "2025-01-01"


def _in_effect_parameter(parameters, state, folder):
    # ``.children[state]`` avoids the ``in`` keyword problem for Indiana.
    program = getattr(parameters.gov.contrib.states.children[state], folder)
    return program.in_effect


@pytest.fixture(scope="module")
def parameters_all_in_effect():
    # Clone ONLY the gov.contrib.states subtree and turn every state's contrib
    # reform on. We must NOT deep-copy system.parameters (or any subtree as-is):
    # every ParameterNode/Parameter holds a ``parent`` back-reference, so the
    # copy escapes upward and duplicates the whole tree (~1 GB peak), which
    # OOM-killed the CI runner. Clearing the cloned root's parent keeps updates
    # contained without mutating the global parameter tree.
    # The factories only read their own state's in_effect flag under
    # gov.contrib.states and never touch the parent, so a thin namespace
    # exposing the copied subtree is sufficient.
    states_node = system.parameters.gov.contrib.states
    states_copy = states_node.clone()
    states_copy.parent = None

    parameters = SimpleNamespace(
        gov=SimpleNamespace(contrib=SimpleNamespace(states=states_copy))
    )
    for state, folder, _module, _fn in STATE_CONFIGS:
        _in_effect_parameter(parameters, state, folder).update(
            period="year:2025:1", value=True
        )
    return parameters


@pytest.mark.parametrize(
    "state,folder,module_name,fn_name",
    STATE_CONFIGS,
    ids=[cfg[0] for cfg in STATE_CONFIGS],
)
def test__given_in_effect_true__then_factory_returns_reform_subclass(
    state, folder, module_name, fn_name, parameters_all_in_effect
):
    # Given a parameters tree where the contrib in_effect flag is set true.
    reform_fn = _load_reform_fn(state, folder, module_name, fn_name)

    # When the factory is invoked the way reforms.py invokes it.
    result = reform_fn(parameters_all_in_effect, PERIOD)

    # Then it activates the reform (the non-bypass branch), returning a Reform
    # subclass rather than None.
    assert result is not None, f"{state}: expected a Reform, got None"
    assert isinstance(result, type) and issubclass(result, Reform), (
        f"{state}: expected a Reform subclass, got {result!r}"
    )


@pytest.mark.parametrize(
    "state,folder,module_name,fn_name",
    STATE_CONFIGS,
    ids=[cfg[0] for cfg in STATE_CONFIGS],
)
def test__given_in_effect_false_default__then_factory_returns_none(
    state, folder, module_name, fn_name
):
    # Given the default parameters tree (in_effect is false for every year).
    # No copy needed: the factories only read in_effect and never mutate.
    reform_fn = _load_reform_fn(state, folder, module_name, fn_name)

    # When the factory is invoked.
    result = reform_fn(system.parameters, PERIOD)

    # Then no reform is applied (the no-op default branch).
    assert result is None, f"{state}: expected None, got {result!r}"
