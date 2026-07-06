"""Regression tests for the Idaho and Georgia CTC contributed reforms under a
DELAYED ``in_effect`` activation date (PolicyEngine/policyengine-us#8899).

The YAML tests for these reforms can only set contrib parameters as scalars
(one value for every period), so they cannot express "``in_effect`` turns on in
2028" and never exercised the pre-activation years. Two leaks hid behind that
gap:

* ``ga_refundable_ctc`` had no per-period ``in_effect`` gate, so once the reform
  was installed (the factory installs it for the whole simulation whenever the
  toggle is true in any of the next five years) it paid the refund in every
  year, including pre-activation ones.
* the Idaho reform's ``modify_parameters`` revived ``id_ctc`` in the ordered
  nonrefundable list from a hardcoded ``2026-01-01`` regardless of the actual
  activation date, so the revived nonrefundable credit applied before the
  reform turned on.

These tests drive a multi-year simulation with the toggle set true only from
2028 and assert the reform is inert in the 2026 pre-activation year and active
in 2028.
"""

from policyengine_core.periods import instant
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

ACTIVATION_YEAR = "2028-01-01"


def _activate_from_2028(param_path):
    """A user reform that sets the given boolean contrib parameter true from
    2028 onward (mirroring how the app applies a contrib toggle)."""

    class ActivateFrom2028(Reform):
        def apply(self):
            def modify(parameters):
                node = parameters
                for part in param_path.split("."):
                    node = getattr(node, part)
                node.update(
                    start=instant(ACTIVATION_YEAR),
                    stop=instant("2100-12-31"),
                    value=True,
                )
                return parameters

            self.modify_parameters(modify)

    return ActivateFrom2028


GA_SITUATION = {
    "people": {
        "parent": {"age": {"2026": 30, "2028": 30}},
        "child": {
            "age": {"2026": 2, "2028": 4},
            "ctc_qualifying_child": {"2026": True, "2028": True},
        },
    },
    "tax_units": {
        "tax_unit": {
            "members": ["parent", "child"],
            "filing_status": {"2026": "SINGLE", "2028": "SINGLE"},
            "ga_income_tax_before_non_refundable_credits": {"2026": 0, "2028": 0},
        }
    },
    "households": {
        "household": {
            "members": ["parent", "child"],
            "state_code": {"2026": "GA", "2028": "GA"},
        }
    },
}

ID_SITUATION = {
    "people": {
        "parent": {"age": {"2026": 30, "2028": 30}},
        "child1": {
            "age": {"2026": 2, "2028": 4},
            "ctc_qualifying_child": {"2026": True, "2028": True},
        },
        "child2": {
            "age": {"2026": 4, "2028": 6},
            "ctc_qualifying_child": {"2026": True, "2028": True},
        },
    },
    "tax_units": {
        "tax_unit": {
            "members": ["parent", "child1", "child2"],
            "filing_status": {"2026": "SINGLE", "2028": "SINGLE"},
            "id_income_tax_before_non_refundable_credits": {
                "2026": 1_000,
                "2028": 1_000,
            },
        }
    },
    "households": {
        "household": {
            "members": ["parent", "child1", "child2"],
            "state_code": {"2026": "ID", "2028": "ID"},
        }
    },
}


def _simulation(situation, param_path):
    # start_instant must be the earliest simulated year so the structural-reform
    # factory sees the full window (this is the documented start_instant patch).
    return Simulation(
        situation=situation,
        reform=_activate_from_2028(param_path),
        start_instant="2026-01-01",
    )


def test__ga_refundable_ctc_does_not_leak_before_activation():
    sim = _simulation(GA_SITUATION, "gov.contrib.states.ga.ctc.refundable.in_effect")
    # Pre-activation (2026): no refund.
    assert sim.calculate("ga_refundable_ctc", 2026)[0] == 0
    # Activation year (2028): full $250 per-child refund pays out.
    assert sim.calculate("ga_refundable_ctc", 2028)[0] == 250


def test__id_ctc_revival_does_not_leak_before_activation():
    sim = _simulation(ID_SITUATION, "gov.contrib.states.id.ctc.in_effect")
    # id_ctc always computes the worksheet amount (2 * 205 = 410)...
    assert sim.calculate("id_ctc", 2026)[0] == 410
    # ...but the revival must NOT apply it in the pre-activation year.
    assert sim.calculate("id_non_refundable_credits", 2026)[0] == 0
    # In the activation year the revived nonrefundable credit applies.
    assert sim.calculate("id_non_refundable_credits", 2028)[0] == 410
