"""Unit tests for the pre-OBBBA SNAP ABAWD work requirements autoloader.

YAML tests force-apply the reform via the `reforms:` directive, which
bypasses `create_pre_obbba_snap_abawd_work_requirements_reform`. These
tests exercise the autoloader directly: the bypass flag, the
default-inactive return-None path, and the 5-year forward-lookahead
window. The lookahead cases use a lightweight parameter stub because
constructing real parameter trees with future-dated toggles requires a
`copy.deepcopy(system.parameters)` per case, which pushes peak memory
past the CI runner cap when this directory's batch runs.
"""

from types import SimpleNamespace

from policyengine_us.reforms.snap.pre_obbba_snap_abawd_work_requirements import (
    create_pre_obbba_snap_abawd_work_requirements_reform,
)
from policyengine_us.system import system


def _stub_parameters(in_effect_start_year):
    """Parameter-tree stub whose in_effect toggle turns true at a given year."""

    def node(period):
        return SimpleNamespace(in_effect=period.start.year >= in_effect_start_year)

    return SimpleNamespace(
        gov=SimpleNamespace(
            contrib=SimpleNamespace(
                snap=SimpleNamespace(pre_obbba_abawd_work_requirements=node)
            )
        )
    )


def test_autoloader_returns_none_when_in_effect_false_throughout_window():
    """Default parameters: in_effect is false for all years; autoloader returns None."""
    result = create_pre_obbba_snap_abawd_work_requirements_reform(
        system.parameters, "2026"
    )
    assert result is None


def test_bypass_flag_skips_lookahead_and_returns_reform():
    """bypass=True returns the reform without checking in_effect."""
    result = create_pre_obbba_snap_abawd_work_requirements_reform(
        None, None, bypass=True
    )
    assert result is not None


def test_autoloader_activates_when_in_effect_true_at_simulation_year():
    """in_effect true at the simulated year activates on the first lookahead step."""
    result = create_pre_obbba_snap_abawd_work_requirements_reform(
        _stub_parameters(2026), "2026"
    )
    assert result is not None


def test_autoloader_activates_when_in_effect_true_at_window_edge():
    """in_effect true four years out (last year of the 5-year window) activates."""
    result = create_pre_obbba_snap_abawd_work_requirements_reform(
        _stub_parameters(2030), "2026"
    )
    assert result is not None


def test_autoloader_returns_none_when_in_effect_true_beyond_window():
    """in_effect true five years out (past the 5-year window) does not activate."""
    result = create_pre_obbba_snap_abawd_work_requirements_reform(
        _stub_parameters(2031), "2026"
    )
    assert result is None
